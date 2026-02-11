"""Project management commands."""

import os
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

from dbx_python_cli.commands.repo_utils import get_base_dir, get_config
from dbx_python_cli.commands.venv_utils import get_venv_info
from dbx_python_cli.commands.install import install_package, install_frontend_if_exists

app = typer.Typer(
    help="Project management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)


def get_newest_project(projects_dir: Path) -> tuple[str, Path]:
    """
    Get the newest project from the projects directory.

    Returns:
        tuple: (project_name, project_path)

    Raises:
        typer.Exit: If no projects are found
    """
    if not projects_dir.exists():
        typer.echo(f"❌ Projects directory not found at {projects_dir}", err=True)
        typer.echo("\nCreate a project using: dbx project add <name>")
        raise typer.Exit(code=1)

    # Find all projects (directories with pyproject.toml)
    projects = []
    for item in projects_dir.iterdir():
        if item.is_dir() and (item / "pyproject.toml").exists():
            projects.append(item)

    if not projects:
        typer.echo(f"❌ No projects found in {projects_dir}", err=True)
        typer.echo("\nCreate a project using: dbx project add <name>")
        raise typer.Exit(code=1)

    # Sort by modification time (newest first)
    projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    project_path = projects[0]
    project_name = project_path.name

    return project_name, project_path


@app.callback(invoke_without_command=True)
def project_callback(
    ctx: typer.Context,
    list_projects: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all projects in the projects directory",
    ),
):
    """Project management commands."""
    if list_projects:
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"

        if not projects_dir.exists():
            typer.echo(f"Projects directory: {projects_dir}\n")
            typer.echo("No projects directory found.")
            typer.echo("\nCreate a project using: dbx project add <name>")
            raise typer.Exit(0)

        # Find all projects (directories with pyproject.toml)
        projects = []
        for item in projects_dir.iterdir():
            if item.is_dir() and (item / "pyproject.toml").exists():
                projects.append(item.name)

        if not projects:
            typer.echo(f"Projects directory: {projects_dir}\n")
            typer.echo("No projects found.")
            typer.echo("\nCreate a project using: dbx project add <name>")
            raise typer.Exit(0)

        typer.echo(f"Projects directory: {projects_dir}\n")
        typer.echo(f"Found {len(projects)} project(s):\n")
        for project in sorted(projects):
            project_path = projects_dir / project
            has_frontend = (project_path / "frontend").exists()
            frontend_marker = " 🎨" if has_frontend else ""
            typer.echo(f"  • {project}{frontend_marker}")

        if any((projects_dir / p / "frontend").exists() for p in projects):
            typer.echo("\n🎨 = has frontend")

        raise typer.Exit(0)


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
    auto_install: bool = typer.Option(
        True,
        "--install/--no-install",
        help="Automatically install the project after creation (default: True)",
    ),
):
    """
    Create a new Django project using bundled templates.
    Frontend is added by default. Use --no-frontend to skip frontend creation.

    Projects are created in base_dir/projects/ by default.

    Examples::

        dbx project add myproject          # Create with explicit name (includes frontend)
        dbx project add myproject --no-frontend  # Create without frontend
        dbx project add --random           # Create with random name (includes frontend)
        dbx project add -r                 # Short form
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
        typer.echo("❌ Error: Project name is required", err=True)
        typer.echo("\nUsage: dbx project add <name> [OPTIONS]")
        typer.echo("   or: dbx project add --random [OPTIONS]")
        raise typer.Exit(code=1)

    # Use project name as default settings module
    settings_path = f"settings.{name}"

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
                cwd=str(project_path.parent),
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

            # Also show stdout if available for debugging
            if result.stdout:
                typer.echo(f"   Output: {result.stdout.strip()}", err=True)

            raise typer.Exit(code=result.returncode)

    # Verify the project directory was created
    if not project_path.exists():
        typer.echo(
            f"❌ Project directory was not created at {project_path}. "
            "The django-admin command may have failed silently.",
            err=True,
        )
        if result.stdout:
            typer.echo(f"   django-admin stdout: {result.stdout.strip()}", err=True)
        if result.stderr:
            typer.echo(f"   django-admin stderr: {result.stderr.strip()}", err=True)
        raise typer.Exit(code=1)

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

    # Automatically install the project if requested
    if auto_install:
        typer.echo(f"\n📦 Installing project '{name}'...")
        try:
            # Get the virtual environment info
            python_path, venv_type = get_venv_info(project_path, None)

            if venv_type == "system":
                typer.echo(
                    "⚠️  Warning: No virtual environment detected. Installing to system Python.",
                    err=True,
                )

            # Install the Python package
            result = install_package(
                project_path,
                python_path,
                install_dir=None,
                extras=None,
                groups=None,
                verbose=False,
            )

            if result == "success":
                typer.echo("✅ Python package installed successfully")
            elif result == "skipped":
                typer.echo(
                    "⚠️  Installation skipped (no pyproject.toml found)", err=True
                )
            else:
                typer.echo("⚠️  Python package installation failed", err=True)

            # Install frontend dependencies if frontend exists
            if add_frontend:
                frontend_installed = install_frontend_if_exists(
                    project_path, verbose=False
                )
                if not frontend_installed and (project_path / "frontend").exists():
                    typer.echo(
                        "⚠️  Frontend installation failed or npm not found",
                        err=True,
                    )
        except Exception as e:
            typer.echo(
                f"⚠️  Project created successfully, but installation failed: {e}",
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
    name: str = typer.Argument(None, help="Project name (defaults to newest project)"),
    directory: Path = typer.Option(
        None,
        "--directory",
        "-d",
        help="Custom directory where the project is located (defaults to base_dir/projects/)",
    ),
):
    """Delete a Django project by name.

    If no project name is provided, removes the most recently created project.
    This will first attempt to uninstall the project package using pip in the
    current Python environment, then remove the project directory.

    Examples::

        dbx project remove                # Remove newest project
        dbx project remove myproject      # Remove specific project
    """
    # Determine project directory
    if directory is None:
        # Use base_dir/projects/ as default
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"

        # If no name provided, find the newest project
        if name is None:
            name, target = get_newest_project(projects_dir)
            typer.echo(f"ℹ️  No project specified, using newest: '{name}'")
        else:
            target = projects_dir / name
    else:
        if name is None:
            typer.echo("❌ Project name is required when using --directory", err=True)
            raise typer.Exit(code=1)
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


@app.command("run")
def run_project(
    name: str = typer.Argument(None, help="Project name (defaults to newest project)"),
    directory: Path = typer.Option(
        None,
        "--directory",
        "-d",
        help="Custom directory where the project is located (defaults to base_dir/projects/)",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Host to bind the Django server to",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to bind the Django server to",
    ),
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (defaults to project name, e.g., 'base', 'qe')",
    ),
):
    """
    Run a Django project with manage.py runserver.

    If no project name is provided, runs the most recently created project.
    If a frontend directory exists, it will be run automatically alongside the Django server.

    Examples::

        dbx project run                      # Run newest project
        dbx project run myproject
        dbx project run myproject --settings base
        dbx project run myproject -s qe --port 8080
    """
    import os
    import signal

    # Determine project directory
    if directory is None:
        # Use base_dir/projects/ as default
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"

        # If no name provided, find the newest project
        if name is None:
            name, project_path = get_newest_project(projects_dir)
            typer.echo(f"ℹ️  No project specified, using newest: '{name}'")
        else:
            project_path = projects_dir / name
    else:
        if name is None:
            typer.echo("❌ Project name is required when using --directory", err=True)
            raise typer.Exit(code=1)
        project_path = directory / name

    if not project_path.exists():
        typer.echo(f"❌ Project '{name}' not found at {project_path}", err=True)
        raise typer.Exit(code=1)

    # Check if frontend exists
    frontend_path = project_path / "frontend"
    has_frontend = frontend_path.exists() and (frontend_path / "package.json").exists()

    typer.echo(f"🚀 Running project '{name}' on http://{host}:{port}")

    # Set up environment
    env = os.environ.copy()

    # Check for default environment variables from config
    config = get_config()
    default_env = config.get("project", {}).get("default_env", {})

    # Set MONGODB_URI if not in environment
    if "MONGODB_URI" not in env:
        default_uri = default_env.get("MONGODB_URI")
        if default_uri:
            typer.echo(f"🔗 Using default MongoDB URI from config: {default_uri}")
            env["MONGODB_URI"] = default_uri

    # Set library paths for libmongocrypt (Queryable Encryption support)
    for var in ["PYMONGOCRYPT_LIB", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"]:
        if var not in env and var in default_env:
            value = os.path.expanduser(default_env[var])
            env[var] = value
            typer.echo(f"🔧 Using {var} from config: {value}")

    # Default to project_name.py settings if not specified
    settings_module = settings if settings else name
    env["DJANGO_SETTINGS_MODULE"] = f"{name}.settings.{settings_module}"
    env["PYTHONPATH"] = str(project_path) + os.pathsep + env.get("PYTHONPATH", "")
    typer.echo(f"🔧 Using DJANGO_SETTINGS_MODULE={env['DJANGO_SETTINGS_MODULE']}")

    if has_frontend:
        # Ensure frontend is installed
        typer.echo("📦 Checking frontend dependencies...")
        try:
            _install_npm(name, directory=project_path.parent)
        except Exception as e:
            typer.echo(f"⚠️  Frontend installation check failed: {e}", err=True)
            # Continue anyway - frontend might already be installed

        # Start frontend process in background
        typer.echo("🎨 Starting frontend development server...")
        frontend_proc = subprocess.Popen(
            ["npm", "run", "watch"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Handle CTRL-C to kill both processes
        def signal_handler(signum, frame):
            typer.echo("\n🛑 Stopping servers...")
            frontend_proc.terminate()
            raise KeyboardInterrupt

        signal.signal(signal.SIGINT, signal_handler)

        try:
            typer.echo("🌐 Starting Django development server...")
            subprocess.run(
                [sys.executable, "manage.py", "runserver", f"{host}:{port}"],
                cwd=project_path,
                env=env,
                check=True,
            )
        except KeyboardInterrupt:
            typer.echo("\n✅ Servers stopped")
        finally:
            if frontend_proc.poll() is None:
                frontend_proc.terminate()
                frontend_proc.wait()
    else:
        # No frontend - just run Django
        try:
            typer.echo("🌐 Starting Django development server...")
            subprocess.run(
                [sys.executable, "manage.py", "runserver", f"{host}:{port}"],
                cwd=project_path,
                env=env,
                check=True,
            )
        except KeyboardInterrupt:
            typer.echo("\n✅ Server stopped")


@app.command("open")
def open_browser(
    host: str = typer.Option("localhost", "--host", "-h", help="Host to open"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to open"),
):
    """
    Open localhost in the browser.

    Examples::

        dbx project open                    # Opens http://localhost:8000
        dbx project open --port 3000        # Opens http://localhost:3000
        dbx project open --host 127.0.0.1   # Opens http://127.0.0.1:8000
    """
    import webbrowser

    url = f"http://{host}:{port}"
    typer.echo(f"🌐 Opening {url} in browser...")

    try:
        webbrowser.open(url)
        typer.echo(f"✅ Opened {url}")
    except Exception as e:
        typer.echo(f"❌ Failed to open browser: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("manage")
def manage(
    name: str = typer.Argument(None, help="Project name (defaults to newest project)"),
    command: str = typer.Argument(None, help="Django management command to run"),
    args: list[str] = typer.Argument(None, help="Additional arguments for the command"),
    directory: Path = typer.Option(
        None,
        "--directory",
        "-d",
        help="Custom directory where the project is located (defaults to base_dir/projects/)",
    ),
    mongodb_uri: str = typer.Option(
        None, "--mongodb-uri", help="MongoDB connection URI"
    ),
    database: str = typer.Option(
        None,
        "--database",
        help="Specify the database to use",
    ),
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (defaults to project name)",
    ),
):
    """
    Run any Django management command for a project.

    If no project name is provided, uses the most recently created project.

    Examples::

        dbx project manage shell                # Run shell on newest project
        dbx project manage myproject shell
        dbx project manage myproject createsuperuser
        dbx project manage myproject --mongodb-uri mongodb+srv://user:pwd@cluster
        dbx project manage myproject --settings base shell
        dbx project manage myproject migrate --database default
    """
    import os

    if args is None:
        args = []

    # Determine project directory
    if directory is None:
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"

        # If no name provided, find the newest project
        if name is None:
            name, project_path = get_newest_project(projects_dir)
            typer.echo(f"ℹ️  No project specified, using newest: '{name}'")
        else:
            project_path = projects_dir / name
    else:
        if name is None:
            typer.echo("❌ Project name is required when using --directory", err=True)
            raise typer.Exit(code=1)
        project_path = directory / name

    if not project_path.exists():
        typer.echo(f"❌ Project '{name}' not found at {project_path}", err=True)
        raise typer.Exit(code=1)

    # Set up environment
    env = os.environ.copy()

    # Check for default environment variables from config
    config = get_config()
    default_env = config.get("project", {}).get("default_env", {})

    if mongodb_uri:
        typer.echo(f"🔗 Using MongoDB URI: {mongodb_uri}")
        env["MONGODB_URI"] = mongodb_uri
    elif "MONGODB_URI" not in env:
        # Check config for default MONGODB_URI
        default_uri = default_env.get("MONGODB_URI")
        if default_uri:
            typer.echo(f"🔗 Using default MongoDB URI from config: {default_uri}")
            env["MONGODB_URI"] = default_uri

    # Set library paths for libmongocrypt (Queryable Encryption support)
    for var in ["PYMONGOCRYPT_LIB", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"]:
        if var not in env and var in default_env:
            value = os.path.expanduser(default_env[var])
            env[var] = value

    # Default to project_name.py settings if not specified
    settings_module = settings if settings else name
    env["DJANGO_SETTINGS_MODULE"] = f"{name}.settings.{settings_module}"
    env["PYTHONPATH"] = str(project_path) + os.pathsep + env.get("PYTHONPATH", "")
    typer.echo(f"🔧 Using DJANGO_SETTINGS_MODULE={env['DJANGO_SETTINGS_MODULE']}")

    # Build command
    cmd_args = []
    if command:
        cmd_args.append(command)
        if database:
            cmd_args.append(f"--database={database}")
        cmd_args.extend(args)
        typer.echo(f"⚙️  Running django-admin {' '.join(cmd_args)} for '{name}'")
    else:
        typer.echo(f"ℹ️  Running django-admin with no arguments for '{name}'")

    try:
        subprocess.run(
            ["django-admin", *cmd_args],
            cwd=project_path.parent,
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Command failed with exit code {e.returncode}", err=True)
        raise typer.Exit(code=e.returncode)
    except FileNotFoundError:
        typer.echo(
            "❌ 'django-admin' command not found. Make sure Django is installed.",
            err=True,
        )
        raise typer.Exit(code=1)


@app.command("su")
def create_superuser(
    name: str = typer.Argument(None, help="Project name (defaults to newest project)"),
    directory: Path = typer.Option(
        None,
        "--directory",
        "-d",
        help="Custom directory where the project is located (defaults to base_dir/projects/)",
    ),
    username: str = typer.Option(
        "admin", "--username", "-u", help="Superuser username"
    ),
    password: str = typer.Option(
        "admin", "--password", "-p", help="Superuser password"
    ),
    email: str = typer.Option(
        None,
        "--email",
        "-e",
        help="Superuser email (defaults to $PROJECT_EMAIL if set)",
    ),
    mongodb_uri: str = typer.Option(
        None,
        "--mongodb-uri",
        help="Optional MongoDB connection URI. Falls back to $MONGODB_URI if not provided.",
    ),
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (defaults to project name)",
    ),
):
    """
    Create a Django superuser with no interaction required.

    If no project name is provided, uses the most recently created project.

    Examples::

        dbx project su                          # Create superuser on newest project
        dbx project su myproject
        dbx project su myproject --settings base
        dbx project su myproject -u myuser -p mypass
        dbx project su myproject -e admin@example.com
    """
    import os

    if not email:
        email = os.getenv("PROJECT_EMAIL", "admin@example.com")

    # Determine project directory
    if directory is None:
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"

        # If no name provided, find the newest project
        if name is None:
            name, project_path = get_newest_project(projects_dir)
            typer.echo(f"ℹ️  No project specified, using newest: '{name}'")
        else:
            project_path = projects_dir / name
    else:
        if name is None:
            typer.echo("❌ Project name is required when using --directory", err=True)
            raise typer.Exit(code=1)
        project_path = directory / name

    typer.echo(f"👑 Creating Django superuser '{username}' for project '{name}'")

    if not project_path.exists():
        typer.echo(f"❌ Project '{name}' not found at {project_path}", err=True)
        raise typer.Exit(code=1)

    # Set up environment
    env = os.environ.copy()

    # Check for default environment variables from config
    config = get_config()
    default_env = config.get("project", {}).get("default_env", {})

    if mongodb_uri:
        typer.echo(f"🔗 Using MongoDB URI: {mongodb_uri}")
        env["MONGODB_URI"] = mongodb_uri
    elif "MONGODB_URI" not in env:
        # Check config for default MONGODB_URI
        default_uri = default_env.get("MONGODB_URI")
        if default_uri:
            typer.echo(f"🔗 Using default MongoDB URI from config: {default_uri}")
            env["MONGODB_URI"] = default_uri

    # Set library paths for libmongocrypt (Queryable Encryption support)
    for var in ["PYMONGOCRYPT_LIB", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"]:
        if var not in env and var in default_env:
            value = os.path.expanduser(default_env[var])
            env[var] = value

    env["DJANGO_SUPERUSER_PASSWORD"] = password

    # Default to project_name.py settings if not specified
    settings_module = settings if settings else name
    env["DJANGO_SETTINGS_MODULE"] = f"{name}.settings.{settings_module}"
    env["PYTHONPATH"] = str(project_path) + os.pathsep + env.get("PYTHONPATH", "")
    typer.echo(f"🔧 Using DJANGO_SETTINGS_MODULE={env['DJANGO_SETTINGS_MODULE']}")

    try:
        subprocess.run(
            [
                "django-admin",
                "createsuperuser",
                "--noinput",
                f"--username={username}",
                f"--email={email}",
            ],
            cwd=project_path.parent,
            env=env,
            check=True,
        )
        typer.echo(f"✅ Superuser '{username}' created successfully")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Command failed with exit code {e.returncode}", err=True)
        raise typer.Exit(code=e.returncode)
    except FileNotFoundError:
        typer.echo(
            "❌ 'django-admin' command not found. Make sure Django is installed.",
            err=True,
        )
        raise typer.Exit(code=1)


@app.command("edit")
def edit_project(
    name: str = typer.Argument(None, help="Project name (defaults to newest project)"),
    directory: Path = typer.Option(
        None,
        "--directory",
        "-d",
        help="Custom directory where the project is located (defaults to base_dir/projects/)",
    ),
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to edit (e.g., 'base', 'qe', or project name). Defaults to project name.",
    ),
):
    """
    Edit project settings file with your default editor.

    Opens the project's settings file using the editor specified in the EDITOR
    environment variable. If EDITOR is not set, falls back to common editors
    (vim, nano, vi) or uses 'open' on macOS.

    If no project name is provided, uses the most recently created project.

    Examples::

        dbx project edit                      # Edit newest project's settings
        dbx project edit myproject            # Edit myproject's settings
        dbx project edit myproject --settings base  # Edit base settings
        dbx project edit myproject -s qe      # Edit qe settings
        EDITOR=code dbx project edit          # Open with VS Code
    """
    # Determine project directory
    if directory is None:
        config = get_config()
        base_dir = get_base_dir(config)
        projects_dir = base_dir / "projects"

        # If no name provided, find the newest project
        if name is None:
            name, project_path = get_newest_project(projects_dir)
            typer.echo(f"ℹ️  No project specified, using newest: '{name}'")
        else:
            project_path = projects_dir / name
    else:
        if name is None:
            typer.echo("❌ Project name is required when using --directory", err=True)
            raise typer.Exit(code=1)
        project_path = directory / name

    if not project_path.exists():
        typer.echo(f"❌ Project '{name}' not found at {project_path}", err=True)
        raise typer.Exit(code=1)

    # Determine which settings file to edit
    settings_module = settings if settings else name
    settings_file = project_path / name / "settings" / f"{settings_module}.py"

    if not settings_file.exists():
        typer.echo(f"❌ Settings file not found: {settings_file}", err=True)
        typer.echo(f"\nAvailable settings files in {project_path / name / 'settings'}:")
        settings_dir = project_path / name / "settings"
        if settings_dir.exists():
            for file in settings_dir.glob("*.py"):
                if file.name != "__init__.py":
                    typer.echo(f"  • {file.stem}")
        raise typer.Exit(code=1)

    # Get editor from environment variable
    editor = os.environ.get("EDITOR")

    if not editor:
        # Try common editors in order of preference
        common_editors = ["vim", "nano", "vi"]
        for candidate in common_editors:
            try:
                # Check if editor exists in PATH
                subprocess.run(
                    ["which", candidate],
                    check=True,
                    capture_output=True,
                )
                editor = candidate
                break
            except subprocess.CalledProcessError:
                continue

        # If no common editor found, try 'open' on macOS
        if not editor:
            import platform

            if platform.system() == "Darwin":
                editor = "open"
            else:
                typer.echo(
                    "❌ No editor found. Please set the EDITOR environment variable.",
                    err=True,
                )
                typer.echo("\nExample: export EDITOR=nano")
                raise typer.Exit(1)

    typer.echo(f"📝 Opening {settings_file} with {editor}...")

    try:
        # Open the editor
        result = subprocess.run([editor, str(settings_file)])

        if result.returncode == 0:
            typer.echo("✅ Settings file saved")
        else:
            typer.echo(
                f"⚠️  Editor exited with code {result.returncode}",
                err=True,
            )
            raise typer.Exit(result.returncode)
    except FileNotFoundError:
        typer.echo(
            f"❌ Editor '{editor}' not found. Please check your EDITOR environment variable.",
            err=True,
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        typer.echo("\n⚠️  Editing cancelled")
        raise typer.Exit(130)


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
