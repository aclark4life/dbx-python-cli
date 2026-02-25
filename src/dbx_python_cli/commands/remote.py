"""Remote command for showing git remotes."""

import subprocess
from pathlib import Path

import typer

from dbx_python_cli.commands.repo_utils import (
    find_all_repos,
    find_repo_by_name,
    get_base_dir,
    get_config,
    get_repo_groups,
)

# Create a Typer app that will act as a single command
app = typer.Typer(
    help="Show git remotes",
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def remote_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to show remotes for"),
    group: str = typer.Option(
        None,
        "--group",
        "-g",
        help="Show remotes for all repositories in a group",
    ),
    project: str = typer.Option(
        None,
        "--project",
        "-p",
        help="Show remotes for a project",
    ),
):
    """Show git remotes from a repository or group of repositories.

    Usage::

        dbx remote <repo_name>           # Show remote names
        dbx remote -v <repo_name>        # Show remote names and URLs
        dbx remote -g <group>            # Show remotes for all repos in group

    Examples::

        dbx remote mongo-python-driver   # Show remote names
        dbx remote -v mongo-python-driver  # Show remote names and URLs
        dbx remote -g pymongo            # Show remotes for all pymongo repos
    """
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

    # Handle group option
    if group:
        groups = get_repo_groups(config)
        if group not in groups:
            typer.echo(
                f"❌ Error: Group '{group}' not found in configuration.", err=True
            )
            typer.echo(f"Available groups: {', '.join(groups.keys())}", err=True)
            raise typer.Exit(1)

        # Find all repos in the group
        all_repos = find_all_repos(base_dir)
        group_repos = [r for r in all_repos if r["group"] == group]

        if not group_repos:
            typer.echo(
                f"❌ Error: No repositories found for group '{group}'.", err=True
            )
            typer.echo(f"\nClone repositories using: dbx clone -g {group}")
            raise typer.Exit(1)

        typer.echo(
            f"Showing remotes for {len(group_repos)} repository(ies) in group '{group}':\n"
        )

        for repo_info in group_repos:
            _run_git_remote(repo_info["path"], repo_info["name"], verbose)
            typer.echo("")  # Add blank line between repos

        return

    # Handle project option
    if project:
        projects_dir = base_dir / "projects"
        project_path = projects_dir / project

        if not project_path.exists():
            typer.echo(
                f"❌ Error: Project '{project}' not found at {project_path}", err=True
            )
            raise typer.Exit(1)

        _run_git_remote(project_path, project, verbose)
        return

    # Require repo_name if not listing, not using group, and not using project
    if not repo_name:
        typer.echo("❌ Error: Repository name, group, or project is required", err=True)
        typer.echo("\nUsage: dbx remote <repo_name>")
        typer.echo("   or: dbx remote -g <group>")
        typer.echo("   or: dbx remote -p <project>")
        typer.echo("   or: dbx list")
        raise typer.Exit(1)

    # Find the repository
    repo = find_repo_by_name(repo_name, base_dir)
    if not repo:
        typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
        typer.echo("\nRun 'dbx list' to see available repositories")
        raise typer.Exit(1)

    repo_path = Path(repo["path"])
    _run_git_remote(repo_path, repo_name, verbose)


def _run_git_remote(repo_path: Path, name: str, verbose: bool = False):
    """Run git remote in a repository or project."""
    # Check if it's a git repository
    if not (repo_path / ".git").exists():
        typer.echo(f"⚠️  {name}: Not a git repository (skipping)", err=True)
        return

    # Build git remote command
    git_cmd = ["git", "remote"]
    if verbose:
        git_cmd.append("-v")
        typer.echo(f"🔗 {name}: Remotes (with URLs)")
    else:
        typer.echo(f"🔗 {name}: Remotes")

    # Run git remote in the repository
    result = subprocess.run(
        git_cmd,
        cwd=str(repo_path),
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        if result.stdout.strip():
            typer.echo(result.stdout.strip())
        else:
            typer.echo("  (no remotes configured)")
    else:
        typer.echo(f"⚠️  {name}: git remote failed", err=True)
        if result.stderr:
            typer.echo(f"   {result.stderr.strip()}", err=True)
