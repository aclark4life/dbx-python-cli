"""Install command for installing dependencies in repositories."""

import subprocess
from pathlib import Path
from typing import Optional

import typer

from dbx_python_cli.commands.repo import get_base_dir, get_config

app = typer.Typer(
    help="Install commands",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": False,
    },
    no_args_is_help=False,
)


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


@app.callback(
    invoke_without_command=True, context_settings={"allow_interspersed_args": True}
)
def install_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(
        None, help="Repository name to install dependencies for"
    ),
    extras: Optional[str] = typer.Option(
        None,
        "--extras",
        "-e",
        help="Comma-separated list of extras to install (e.g., 'test', 'dev', 'aws')",
    ),
    groups: Optional[str] = typer.Option(
        None,
        "--groups",
        "-g",
        help="Comma-separated list of dependency groups to install (e.g., 'dev', 'test')",
    ),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available repositories",
    ),
):
    """Install dependencies in a cloned repository using uv pip install."""
    # If a subcommand was invoked, don't run this logic
    if ctx.invoked_subcommand is not None:
        return

    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Config: {config}\n")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

    # Handle --list flag
    if list_repos:
        repos = find_all_repos(base_dir)
        if not repos:
            typer.echo("No repositories found.")
            typer.echo("\nClone repositories using: dbx repo clone -g <group>")
            return

        typer.echo("Available repositories:\n")
        for repo in repos:
            typer.echo(f"  • {repo['name']} ({repo['group']})")
        return

    # Require repo_name if not listing
    if not repo_name:
        typer.echo("❌ Error: Repository name is required", err=True)
        typer.echo("\nUsage: dbx install <repo_name> [OPTIONS]")
        typer.echo("       dbx install --list")
        raise typer.Exit(1)

    # Find the repository
    repo = find_repo_by_name(repo_name, base_dir)
    if not repo:
        typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
        typer.echo("\nRun 'dbx install --list' to see available repositories")
        raise typer.Exit(1)

    repo_path = Path(repo["path"])

    # Build the install command
    install_spec = "."

    # Add extras if specified
    if extras:
        extras_list = [e.strip() for e in extras.split(",")]
        install_spec = f".[{','.join(extras_list)}]"

    # Install the package with extras
    typer.echo(f"Installing dependencies in {repo_path}...\n")

    install_cmd = ["uv", "pip", "install", "-e", install_spec]

    if verbose:
        typer.echo(f"[verbose] Running command: {' '.join(install_cmd)}")
        typer.echo(f"[verbose] Working directory: {repo_path}\n")

    install_result = subprocess.run(
        install_cmd,
        cwd=str(repo_path),
        check=False,
        capture_output=not verbose,  # Show output in real-time if verbose
        text=True,
    )

    if install_result.returncode != 0:
        typer.echo("⚠️  Warning: Installation failed", err=True)
        if not verbose and install_result.stderr:
            typer.echo(install_result.stderr, err=True)
        raise typer.Exit(1)
    else:
        typer.echo("✅ Package installed successfully\n")
        if verbose and install_result.stdout:
            typer.echo(f"[verbose] Output:\n{install_result.stdout}")

    # Install dependency groups if specified
    if groups:
        groups_list = [g.strip() for g in groups.split(",")]
        typer.echo(f"Installing dependency groups: {', '.join(groups_list)}...\n")

        for group in groups_list:
            group_cmd = ["uv", "pip", "install", "--group", group]

            if verbose:
                typer.echo(f"[verbose] Running command: {' '.join(group_cmd)}")
                typer.echo(f"[verbose] Working directory: {repo_path}\n")

            group_result = subprocess.run(
                group_cmd,
                cwd=str(repo_path),
                check=False,
                capture_output=not verbose,  # Show output in real-time if verbose
                text=True,
            )

            if group_result.returncode != 0:
                typer.echo(f"⚠️  Warning: Failed to install group '{group}'", err=True)
                if not verbose and group_result.stderr:
                    typer.echo(group_result.stderr, err=True)
            else:
                typer.echo(f"✅ Group '{group}' installed successfully")
                if verbose and group_result.stdout:
                    typer.echo(f"[verbose] Output:\n{group_result.stdout}")

        typer.echo()  # Empty line at the end
