"""Repository management commands."""

import subprocess
import tomllib
from pathlib import Path

import typer

app = typer.Typer(help="Repository management commands")


def get_config():
    """Load configuration from pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def get_base_dir(config):
    """Get the base directory for cloning repos."""
    base_dir = (
        config.get("tool", {}).get("dbx", {}).get("repo", {}).get("base_dir", "~/repos")
    )
    return Path(base_dir).expanduser()


def get_repo_groups(config):
    """Get repository groups from config."""
    return config.get("tool", {}).get("dbx", {}).get("repo", {}).get("groups", {})


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

        # Create base directory if it doesn't exist
        base_dir.mkdir(parents=True, exist_ok=True)
        typer.echo(
            f"Cloning {len(repos)} repository(ies) from group '{group}' to {base_dir}"
        )

        for repo_url in repos:
            # Extract repo name from URL
            repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
            repo_path = base_dir / repo_name

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

        typer.echo(f"\n✨ Done! Repositories cloned to {base_dir}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
