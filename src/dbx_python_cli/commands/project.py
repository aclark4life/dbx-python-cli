"""Project management commands."""

import random
import shutil
import subprocess
import sys
from pathlib import Path

import typer

try:
    import importlib.resources as resources
except ImportError:
    import importlib_resources as resources

from dbx_python_cli.commands.repo import get_base_dir, get_config

app = typer.Typer(
    help="Project management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)

# Constants for random name generation
ADJECTIVES = [
    "happy",
    "sunny",
    "clever",
    "brave",
    "calm",
    "bright",
    "swift",
    "gentle",
    "mighty",
    "noble",
    "quiet",
    "wise",
    "bold",
    "keen",
    "lively",
    "merry",
    "proud",
    "quick",
    "smart",
    "strong",
]
NOUNS = [
    "panda",
    "eagle",
    "tiger",
    "dragon",
    "phoenix",
    "falcon",
    "wolf",
    "bear",
    "lion",
    "hawk",
    "owl",
    "fox",
    "deer",
    "otter",
    "seal",
    "whale",
    "shark",
    "raven",
    "cobra",
    "lynx",
]


def generate_random_project_name():
    """Generate a random project name using adjectives and nouns."""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adjective}_{noun}"


@app.command("add")
def add_project(
    name: str = typer.Argument(
        None, help="Project name (optional if --random is used)"
    ),
    directory: Path = typer.Option(
        None,
        "--directory",
        "-d",
        help="Custom directory to create the project in (defaults to base_dir/projects/)",
    ),
    add_frontend: bool = typer.Option(
        True,
        "--add-frontend/--no-frontend",
        "-f/-F",
        help="Add frontend (default: True)",
    ),
    random_name: bool = typer.Option(
        False,
        "--random",
        "-r",
        help="Generate a random project name. If both name and --random are provided, the name takes precedence.",
    ),
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (e.g., 'qe', 'site1'). Defaults to 'base'.",
    ),
):
    """
    Create a new Django project using bundled templates.
    Frontend is added by default. Use --no-frontend to skip frontend creation.

    Projects are created in base_dir/projects/ by default.

    Examples:
        dbx project add myproject          # Create with explicit name (includes frontend)
        dbx project add myproject --no-frontend  # Create without frontend
        dbx project add --random           # Create with random name (includes frontend)
        dbx project add -r                 # Short form
        dbx project add -r --settings=qe   # Random name with qe settings
        dbx project add myproject --settings=qe  # Explicit name with qe settings
        dbx project add myproject -d ~/custom/path  # Create in custom directory
    """
    # Handle random name generation
    if random_name:
        if name is not None:
            typer.echo(
                "⚠️  Both a project name and --random flag were provided. Using the provided name.",
                err=True,
            )
        else:
            name = generate_random_project_name()
            typer.echo(f"🎲 Generated random project name: {name}")
    elif name is None:
        typer.echo(
            "❌ Project name is required. Provide a name or use --random flag.",
            err=True,
        )
        raise typer.Exit(code=1)

    # Determine settings path
    if settings:
        # Construct settings path from the provided name
        settings_path = f"settings.{settings}"
        typer.echo(f"🔧 Using settings configuration: {settings_path}")
    else:
        settings_path = "settings.base"

    # Determine project directory
    if directory is None:
        # Use base_dir/projects/ as default
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        project_path = projects_dir / name
    else:
        project_path = directory / name

    if project_path.exists():
        typer.echo(f"❌ Project '{name}' already exists at {project_path}", err=True)
        raise typer.Exit(code=1)

    with resources.path(
        "dbx_python_cli.templates", "project_template"
    ) as template_path:
        cmd = [
            "django-admin",
            "startproject",
            "--template",
            str(template_path),
            name,
        ]
        typer.echo(f"📦 Creating project: {name}")

        # Run django-admin in a way that surfaces a clean, user-friendly error
        # instead of a full Python traceback when Django is missing or
        # misconfigured in the current environment.
        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            typer.echo(
                "❌ 'django-admin' command not found. Make sure Django is installed "
                "in this environment and that 'django-admin' is on your PATH.",
                err=True,
            )
            raise typer.Exit(code=1)

        if result.returncode != 0:
            # Try to show a concise reason (e.g. "ModuleNotFoundError: No module named 'django'")
            reason = None
            if result.stderr:
                lines = [
                    line.strip() for line in result.stderr.splitlines() if line.strip()
                ]
                if lines:
                    reason = lines[-1]

            typer.echo(
                "❌ Failed to create project using django-admin. "
                "This usually means Django is not installed or is misconfigured "
                "in the current Python environment.",
                err=True,
            )
            if reason:
                typer.echo(f"   Reason: {reason}", err=True)

            raise typer.Exit(code=result.returncode)

    # Add pyproject.toml after project creation
    _create_pyproject_toml(project_path, name, settings_path)

    # Create frontend by default (unless --no-frontend is specified)
    if add_frontend:
        typer.echo(f"🎨 Adding frontend to project '{name}'...")
        try:
            # Call the internal frontend create helper
            # Pass the parent directory of project_path
            _add_frontend(name, project_path.parent)
        except Exception as e:
            typer.echo(
                f"⚠️  Project created successfully, but frontend creation failed: {e}",
                err=True,
            )


def _create_pyproject_toml(
    project_path: Path, project_name: str, settings_path: str = "settings.base"
):
    """Create a pyproject.toml file for the Django project."""
    pyproject_content = f"""[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A Django project built with DBX Python CLI"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
dependencies = [
    "django-debug-toolbar",
    "django-mongodb-backend",
    "python-webpack-boilerplate",
]

[project.optional-dependencies]
dev = [
    "django-debug-toolbar",
]
test = [
    "pytest",
    "pytest-django",
    "ruff",
]
encryption = [
    "pymongocrypt",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "{project_name}.{settings_path}"
python_files = ["tests.py", "test_*.py", "*_tests.py"]

[tool.setuptools]
packages = ["{project_name}"]
"""

    pyproject_path = project_path / "pyproject.toml"
    try:
        pyproject_path.write_text(pyproject_content)
        typer.echo(
            f"✅ Created pyproject.toml for '{project_name}' with settings: {settings_path}"
        )
    except Exception as e:
        typer.echo(f"⚠️  Failed to create pyproject.toml: {e}", err=True)


def _add_frontend(
    project_name: str,
    directory: Path = Path("."),
):
    """
    Internal helper to create a frontend app inside an existing project.
    """
    project_path = directory / project_name
    name = "frontend"
    if not project_path.exists() or not project_path.is_dir():
        typer.echo(f"❌ Project '{project_name}' not found at {project_path}", err=True)
        raise typer.Exit(code=1)
    # Destination for new app
    app_path = project_path / name
    if app_path.exists():
        typer.echo(
            f"❌ App '{name}' already exists in project '{project_name}'", err=True
        )
        raise typer.Exit(code=1)
    typer.echo(f"📦 Creating app '{name}' in project '{project_name}'")
    # Locate the Django app template directory in package resources
    with resources.path(
        "dbx_python_cli.templates", "frontend_template"
    ) as template_path:
        cmd = [
            "django-admin",
            "startapp",
            "--template",
            str(template_path),
            name,
            str(project_path),
        ]
        subprocess.run(cmd, check=True)


@app.command("remove")
def remove_project(
    name: str,
    directory: Path = typer.Option(
        None,
        "--directory",
        "-d",
        help="Custom directory where the project is located (defaults to base_dir/projects/)",
    ),
):
    """Delete a Django project by name.

    This will first attempt to uninstall the project package using pip in the
    current Python environment, then remove the project directory.
    """
    # Determine project directory
    if directory is None:
        # Use base_dir/projects/ as default
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"
        target = projects_dir / name
    else:
        target = directory / name

    if not target.exists() or not target.is_dir():
        typer.echo(f"❌ Project {name} does not exist at {target}.", err=True)
        return

    # Try to uninstall the package from the current environment before
    # removing the project directory. Failures here are non-fatal so that
    # filesystem cleanup still proceeds.
    uninstall_cmd = [sys.executable, "-m", "pip", "uninstall", "-y", name]
    typer.echo(f"📦 Uninstalling project package '{name}' with pip")
    try:
        result = subprocess.run(uninstall_cmd, check=False)
        if result.returncode != 0:
            typer.echo(
                f"⚠️ pip uninstall exited with code {result.returncode}. "
                "Proceeding to remove project files.",
                err=True,
            )
    except FileNotFoundError:
        typer.echo(
            "⚠️ Could not run pip to uninstall the project package. "
            "Proceeding to remove project files.",
            err=True,
        )

    shutil.rmtree(target)
    typer.echo(f"🗑️ Removed project {name}")


def _install_npm(
    project_name: str,
    frontend_dir: str = "frontend",
    directory: Path = Path("."),
    clean: bool = False,
):
    """
    Internal helper to install npm dependencies in the frontend directory.
    """
    project_path = directory / project_name
    if not project_path.exists():
        typer.echo(
            f"❌ Project '{project_name}' does not exist at {project_path}", err=True
        )
        raise typer.Exit(code=1)

    frontend_path = project_path / frontend_dir
    if not frontend_path.exists():
        typer.echo(
            f"❌ Frontend directory '{frontend_dir}' not found at {frontend_path}",
            err=True,
        )
        raise typer.Exit(code=1)

    package_json = frontend_path / "package.json"
    if not package_json.exists():
        typer.echo(f"❌ package.json not found in {frontend_path}", err=True)
        raise typer.Exit(code=1)

    if clean:
        typer.echo(f"🧹 Cleaning node_modules and package-lock.json in {frontend_path}")
        node_modules = frontend_path / "node_modules"
        package_lock = frontend_path / "package-lock.json"

        if node_modules.exists():
            shutil.rmtree(node_modules)
            typer.echo("  ✓ Removed node_modules")

        if package_lock.exists():
            package_lock.unlink()
            typer.echo("  ✓ Removed package-lock.json")

    typer.echo(f"📦 Installing npm dependencies in {frontend_path}")

    try:
        subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
        typer.echo("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ npm install failed with exit code {e.returncode}", err=True)
        raise typer.Exit(code=e.returncode)
    except FileNotFoundError:
        typer.echo(
            "❌ npm not found. Please ensure Node.js and npm are installed.", err=True
        )
        raise typer.Exit(code=1)
