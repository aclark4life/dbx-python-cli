"""Pull command for pulling updates from remote repositories."""

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
    help="Pull updates from remote repositories",
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "allow_interspersed_args": False,
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def pull_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to pull from"),
    group: str = typer.Option(
        None,
        "--group",
        "-g",
        help="Pull updates for all repositories in a group",
    ),
    rebase: bool = typer.Option(
        False,
        "--rebase",
        "-r",
        help="Rebase instead of merge when pulling",
    ),
):
    """Pull updates from remote repositories.

    Usage::

        dbx pull <repo_name>           # Pull a single repository
        dbx pull -g <group_name>       # Pull all repos in a group
        dbx pull <repo_name> --rebase  # Pull with rebase

    Examples::

        dbx pull django-mongodb-backend        # Pull single repo
        dbx pull -g django                     # Pull all repos in django group
        dbx pull --rebase django-mongodb-backend # Pull with rebase
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

    # Handle group pull
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

        typer.echo(f"Pulling {len(group_repos)} repository(ies) in group '{group}':\n")

        for repo_info in group_repos:
            _run_git_pull(repo_info["path"], repo_info["name"], rebase, verbose)

        typer.echo(f"\n✨ Done! Pulled {len(group_repos)} repository(ies)")
        return

    # Require repo_name if not using group
    if not repo_name:
        typer.echo("❌ Error: Repository name or group is required", err=True)
        typer.echo("\nUsage: dbx pull <repo_name>")
        typer.echo("   or: dbx pull -g <group>")
        raise typer.Exit(1)

    # Find the repository
    repo = find_repo_by_name(repo_name, base_dir)
    if not repo:
        typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
        typer.echo("\nRun 'dbx list' to see available repositories")
        raise typer.Exit(1)

    repo_path = Path(repo["path"])
    _run_git_pull(repo_path, repo_name, rebase, verbose)


def _run_git_pull(
    repo_path: Path, name: str, rebase: bool = False, verbose: bool = False
):
    """Run git pull in a repository."""
    # Check if it's a git repository
    if not (repo_path / ".git").exists():
        typer.echo(f"⚠️  {name}: Not a git repository (skipping)", err=True)
        return

    # Build git pull command
    git_cmd = ["git", "pull"]
    if rebase:
        git_cmd.append("--rebase")

    typer.echo(f"📥 {name}: Pulling updates...")

    if verbose:
        typer.echo(f"[verbose] Running command: {' '.join(git_cmd)}")
        typer.echo(f"[verbose] Working directory: {repo_path}\n")

    # Run git pull in the repository
    result = subprocess.run(
        git_cmd,
        cwd=str(repo_path),
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        typer.echo(
            f"❌ {name}: git pull failed with exit code {result.returncode}", err=True
        )
        if result.stderr:
            typer.echo(f"   {result.stderr.strip()}", err=True)
    else:
        # Show output if there were updates
        if result.stdout.strip():
            if verbose:
                typer.echo(result.stdout.strip())
            # Check if already up to date
            if (
                "Already up to date" in result.stdout
                or "Already up-to-date" in result.stdout
            ):
                typer.echo(f"✅ {name}: Already up to date")
            else:
                typer.echo(f"✅ {name}: Pulled successfully")
        else:
            typer.echo(f"✅ {name}: Already up to date")
