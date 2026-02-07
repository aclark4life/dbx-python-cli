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


def get_install_dirs(config, group_name, repo_name):
    """
    Get install directories for a repository.

    For monorepos, returns a list of subdirectories to install.
    For regular repos, returns None (install from root).

    Args:
        config: Configuration dictionary
        group_name: Name of the group (e.g., 'langchain')
        repo_name: Name of the repository (e.g., 'langchain-mongodb')

    Returns:
        list: List of install directories, or None if not a monorepo
    """
    groups = get_repo_groups(config)
    if group_name not in groups:
        return None

    install_dirs_config = groups[group_name].get("install_dirs", {})
    return install_dirs_config.get(repo_name)


@app.command()
def clone(
    ctx: typer.Context,
    group: str = typer.Option(
        ...,
        "--group",
        "-g",
        help="Repository group to clone (e.g., pymongo, langchain, django)",
    ),
):
    """Clone repositories from a specified group."""
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        groups = get_repo_groups(config)

        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Available groups: {list(groups.keys())}\n")

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
                if verbose:
                    typer.echo(f"  [verbose] URL: {repo_url}")
                    typer.echo(f"  [verbose] Destination: {repo_path}")
                try:
                    subprocess.run(
                        ["git", "clone", repo_url, str(repo_path)],
                        check=True,
                        capture_output=not verbose,  # Show output in real-time if verbose
                        text=True,
                    )
                    typer.echo(f"  ✅ {repo_name} cloned successfully")
                except subprocess.CalledProcessError as e:
                    typer.echo(
                        f"  ❌ Failed to clone {repo_name}: {e.stderr if not verbose else ''}",
                        err=True,
                    )

        typer.echo(f"\n✨ Done! Repositories cloned to {group_dir}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
