"""Reset command for running git reset in repositories."""

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
    help="Git reset commands",
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "allow_interspersed_args": True,
        "ignore_unknown_options": True,
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def reset_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to run git reset in"),
    git_args: list[str] = typer.Argument(
        None,
        help="Git reset arguments (e.g., '--hard', '--soft', 'HEAD~1'). If not provided, runs 'git reset' without arguments.",
    ),
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
        help="Run git reset in all repositories in a group",
    ),
):
    """Run git reset in repositories.

    Usage::

        dbx reset <repo_name> [git_args...]           # Reset a single repository
        dbx reset -g <group_name> [git_args...]       # Reset all repos in a group

    Examples::

        dbx reset my-repo --hard HEAD~1        # Hard reset to previous commit
        dbx reset my-repo --soft HEAD~1        # Soft reset to previous commit
        dbx reset -g django --hard origin/main # Hard reset all django repos to origin/main
        dbx reset my-repo                      # Reset without arguments (unstage all)
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
        all_repos_list = find_all_repos(base_dir)
        group_repos = [r for r in all_repos_list if r["group"] == group]

        if not group_repos:
            typer.echo(
                f"❌ Error: No repositories found for group '{group}'.", err=True
            )
            typer.echo(f"\nClone repositories using: dbx clone -g {group}")
            raise typer.Exit(1)

        typer.echo(
            f"Running git reset in {len(group_repos)} repository(ies) in group '{group}':\n"
        )

        for repo_info in group_repos:
            _run_git_reset(repo_info["path"], repo_info["name"], git_args, verbose)

        typer.echo(f"\n✨ Done! Reset {len(group_repos)} repository(ies)")
        return

    # Require repo_name if not listing and not using group
    if not repo_name:
        typer.echo("❌ Error: Repository name or group is required", err=True)
        typer.echo("\nUsage: dbx reset <repo_name> [git_args...]")
        typer.echo("   or: dbx reset -g <group> [git_args...]")
        typer.echo("   or: dbx reset --list")
        raise typer.Exit(1)

    # Find the repository
    repo = find_repo_by_name(repo_name, base_dir)
    if not repo:
        typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
        typer.echo("\nRun 'dbx reset --list' to see available repositories")
        raise typer.Exit(1)

    repo_path = Path(repo["path"])
    _run_git_reset(repo_path, repo_name, git_args, verbose)


def _run_git_reset(
    repo_path: Path, name: str, git_args: list[str], verbose: bool = False
):
    """Run git reset in a repository."""
    # Check if it's a git repository
    if not (repo_path / ".git").exists():
        typer.echo(f"⚠️  {name}: Not a git repository (skipping)", err=True)
        return

    # Build git reset command
    git_cmd = ["git", "reset"]
    if git_args:
        git_cmd.extend(git_args)
        typer.echo(f"🔄 {name}: git reset {' '.join(git_args)}")
    else:
        typer.echo(f"🔄 {name}: git reset")

    if verbose:
        typer.echo(f"[verbose] Running command: {' '.join(git_cmd)}")
        typer.echo(f"[verbose] Working directory: {repo_path}\n")

    # Run git reset in the repository
    result = subprocess.run(
        git_cmd,
        cwd=str(repo_path),
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        typer.echo(
            f"❌ {name}: git reset failed with exit code {result.returncode}", err=True
        )
        if result.stderr:
            typer.echo(f"   {result.stderr.strip()}", err=True)
    else:
        # Show output if there was any
        if result.stdout.strip():
            typer.echo(result.stdout.strip())
        if result.stderr.strip():
            typer.echo(result.stderr.strip())
        typer.echo(f"✅ {name}: Reset successfully")
