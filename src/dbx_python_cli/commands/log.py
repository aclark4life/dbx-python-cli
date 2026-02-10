"""Log command for showing git commit logs."""

import subprocess
from pathlib import Path

import typer

from dbx_python_cli.commands.repo_utils import get_base_dir, get_config, get_repo_groups
from dbx_python_cli.commands.repo_utils import find_all_repos, find_repo_by_name

# Create a Typer app that will act as a single command
app = typer.Typer(
    help="Show git commit logs",
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "allow_interspersed_args": False,
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def log_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to show logs for"),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Show repository status (cloned vs available)",
    ),
    group: str = typer.Option(
        None,
        "--group",
        "-g",
        help="Show logs for all repositories in a group",
    ),
    project: str = typer.Option(
        None,
        "--project",
        "-p",
        help="Show logs for a project",
    ),
    num_commits: int = typer.Option(
        10,
        "--number",
        "-n",
        help="Number of commits to show (default: 10)",
    ),
    oneline: bool = typer.Option(
        False,
        "--oneline",
        help="Show logs in oneline format",
    ),
):
    """Show git commit logs from a repository or group of repositories.

    Usage:
        dbx log <repo_name>              # Show last 10 commits
        dbx log <repo_name> -n 20        # Show last 20 commits
        dbx log <repo_name> --oneline    # Show in oneline format
        dbx log -g <group>               # Show logs for all repos in group

    Examples:
        dbx log mongo-python-driver      # Show last 10 commits
        dbx log mongo-python-driver -n 5 # Show last 5 commits
        dbx log -g pymongo               # Show logs for all pymongo repos
    """
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
        from dbx_python_cli.commands.repo_utils import list_repos as list_repos_func

        output = list_repos_func(base_dir, config=config)
        if output:
            typer.echo(f"Base directory: {base_dir}\n")
            typer.echo(output)
            typer.echo(
                "\nLegend: ✓ = cloned, ○ = available to clone, ? = cloned but not in config"
            )
        else:
            typer.echo(f"Base directory: {base_dir}\n")
            typer.echo("No repositories found.")
            typer.echo("\nClone repositories using: dbx clone -g <group>")
        return

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
            f"Showing logs for {len(group_repos)} repository(ies) in group '{group}':\n"
        )

        for repo_info in group_repos:
            _run_git_log(
                repo_info["path"], repo_info["name"], num_commits, oneline, verbose
            )
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

        _run_git_log(project_path, project, num_commits, oneline, verbose)
        return

    # Require repo_name if not listing, not using group, and not using project
    if not repo_name:
        typer.echo("❌ Error: Repository name, group, or project is required", err=True)
        typer.echo("\nUsage: dbx log <repo_name> [-n <number>]")
        typer.echo("   or: dbx log -g <group> [-n <number>]")
        typer.echo("   or: dbx log -p <project> [-n <number>]")
        typer.echo("   or: dbx log --list")
        raise typer.Exit(1)

    # Find the repository
    repo = find_repo_by_name(repo_name, base_dir)
    if not repo:
        typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
        typer.echo("\nRun 'dbx log --list' to see available repositories")
        raise typer.Exit(1)

    repo_path = Path(repo["path"])
    _run_git_log(repo_path, repo_name, num_commits, oneline, verbose)


def _run_git_log(
    repo_path: Path,
    name: str,
    num_commits: int = 10,
    oneline: bool = False,
    verbose: bool = False,
):
    """Run git log in a repository or project."""
    # Check if it's a git repository
    if not (repo_path / ".git").exists():
        typer.echo(f"⚠️  {name}: Not a git repository (skipping)", err=True)
        return

    # Build git log command
    git_cmd = ["git", "--no-pager", "log", f"-n{num_commits}"]
    if oneline:
        git_cmd.append("--oneline")

    if oneline:
        typer.echo(f"📜 {name}: Last {num_commits} commits (oneline)")
    else:
        typer.echo(f"📜 {name}: Last {num_commits} commits")

    if verbose:
        typer.echo(f"[verbose] Running command: {' '.join(git_cmd)}")
        typer.echo(f"[verbose] Working directory: {repo_path}\n")

    # Run git log in the repository
    result = subprocess.run(
        git_cmd,
        cwd=str(repo_path),
        check=False,
    )

    if result.returncode != 0:
        typer.echo(f"⚠️  {name}: git log failed", err=True)
