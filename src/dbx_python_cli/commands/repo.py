"""Repository management commands."""

import subprocess
import tomllib
from pathlib import Path

import typer

app = typer.Typer(
    help="Repository management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def get_config_path():
    """Get the path to the user config file."""
    config_dir = Path.home() / ".config" / "dbx-python-cli"
    return config_dir / "config.toml"


def get_default_config_path():
    """Get the path to the default config file shipped with the package."""
    return Path(__file__).parent.parent / "config.toml"


def get_config():
    """Load configuration from user config or default config."""
    user_config_path = get_config_path()
    default_config_path = get_default_config_path()

    # Try user config first
    if user_config_path.exists():
        with open(user_config_path, "rb") as f:
            return tomllib.load(f)

    # Fall back to default config
    if default_config_path.exists():
        with open(default_config_path, "rb") as f:
            return tomllib.load(f)

    # If neither exists, return empty config
    return {}


def get_base_dir(config):
    """Get the base directory for cloning repos."""
    base_dir = config.get("repo", {}).get("base_dir", "~/repos")
    return Path(base_dir).expanduser()


def get_repo_groups(config):
    """Get repository groups from config."""
    return config.get("repo", {}).get("groups", {})


@app.command()
def init():
    """Initialize user configuration file."""
    user_config_path = get_config_path()
    default_config_path = get_default_config_path()

    if user_config_path.exists():
        typer.echo(f"Configuration file already exists at {user_config_path}")
        overwrite = typer.confirm("Do you want to overwrite it?")
        if not overwrite:
            typer.echo("Aborted.")
            raise typer.Exit(0)

    # Create config directory if it doesn't exist
    user_config_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy default config to user config
    if default_config_path.exists():
        import shutil

        shutil.copy(default_config_path, user_config_path)
        typer.echo(f"✅ Configuration file created at {user_config_path}")
        typer.echo("\nYou can now edit this file to customize your repository groups.")
    else:
        typer.echo(
            f"Error: Default configuration not found at {default_config_path}",
            err=True,
        )
        raise typer.Exit(1)


@app.command()
def clone(
    group: str = typer.Option(
        ...,
        "--group",
        "-g",
        help="Repository group to clone (e.g., pymongo, langchain, django)",
    ),
):
    """Clone repositories from a specified group."""
    try:
        config = get_config()
        base_dir = get_base_dir(config)
        groups = get_repo_groups(config)

        if group not in groups:
            typer.echo(f"Error: Group '{group}' not found in configuration.", err=True)
            typer.echo(f"Available groups: {', '.join(groups.keys())}", err=True)
            raise typer.Exit(1)

        repos = groups[group].get("repos", [])
        if not repos:
            typer.echo(f"Error: No repositories defined for group '{group}'.", err=True)
            raise typer.Exit(1)

        # Create group directory under base directory
        group_dir = base_dir / group
        group_dir.mkdir(parents=True, exist_ok=True)
        typer.echo(
            f"Cloning {len(repos)} repository(ies) from group '{group}' to {group_dir}"
        )

        for repo_url in repos:
            # Extract repo name from URL
            repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
            repo_path = group_dir / repo_name

            if repo_path.exists():
                typer.echo(f"  ⏭️  {repo_name} (already exists)")
            else:
                typer.echo(f"  📦 Cloning {repo_name}...")
                try:
                    subprocess.run(
                        ["git", "clone", repo_url, str(repo_path)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    typer.echo(f"  ✅ {repo_name} cloned successfully")
                except subprocess.CalledProcessError as e:
                    typer.echo(
                        f"  ❌ Failed to clone {repo_name}: {e.stderr}", err=True
                    )

        typer.echo(f"\n✨ Done! Repositories cloned to {group_dir}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


def find_all_repos(base_dir):
    """Find all cloned repositories in the base directory."""
    repos = []
    if not base_dir.exists():
        return repos

    # Look for repos in group subdirectories
    for group_dir in base_dir.iterdir():
        if group_dir.is_dir():
            for repo_dir in group_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / ".git").exists():
                    repos.append(
                        {
                            "name": repo_dir.name,
                            "path": repo_dir,
                            "group": group_dir.name,
                        }
                    )
    return repos


def find_repo_by_name(repo_name, base_dir):
    """Find a repository by name in the base directory."""
    all_repos = find_all_repos(base_dir)
    for repo in all_repos:
        if repo["name"] == repo_name:
            return repo
    return None


@app.command()
def test(
    repo_name: str = typer.Argument(None, help="Repository name to test"),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available repositories",
    ),
):
    """Run pytest in a cloned repository."""
    try:
        config = get_config()
        base_dir = get_base_dir(config)

        # List repos if requested
        if list_repos:
            repos = find_all_repos(base_dir)
            if not repos:
                typer.echo(f"No repositories found in {base_dir}")
                typer.echo(
                    "Run 'dbx repo clone -g <group>' to clone repositories first."
                )
                raise typer.Exit(0)

            typer.echo(f"Available repositories in {base_dir}:\n")
            for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
                typer.echo(f"  [{repo['group']}] {repo['name']}")
            raise typer.Exit(0)

        # Require repo_name if not listing
        if not repo_name:
            typer.echo(
                "Error: Please specify a repository name or use --list to see available repos.",
                err=True,
            )
            raise typer.Exit(1)

        # Find the repository
        repo = find_repo_by_name(repo_name, base_dir)
        if not repo:
            typer.echo(f"Error: Repository '{repo_name}' not found.", err=True)
            typer.echo(
                "Run 'dbx repo test --list' to see available repositories.", err=True
            )
            raise typer.Exit(1)

        repo_path = repo["path"]
        typer.echo(f"Running pytest in {repo_path}...\n")

        # Run pytest in the repository
        result = subprocess.run(
            ["pytest"],
            cwd=str(repo_path),
            check=False,
        )

        if result.returncode == 0:
            typer.echo(f"\n✅ Tests passed in {repo_name}")
        else:
            typer.echo(f"\n❌ Tests failed in {repo_name}", err=True)
            raise typer.Exit(result.returncode)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
