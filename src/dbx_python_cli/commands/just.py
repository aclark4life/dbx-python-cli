"""Just command for running just commands in repositories."""

import subprocess
from pathlib import Path

import typer

from dbx_python_cli.commands.repo import get_base_dir, get_config
from dbx_python_cli.commands.repo_utils import find_all_repos, find_repo_by_name

# Create a Typer app that will act as a single command
app = typer.Typer(
    help="Just commands",
    no_args_is_help=False,
    invoke_without_command=True,
    context_settings={"allow_interspersed_args": False},
)


@app.callback()
def just_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to run just in"),
    just_args: list[str] = typer.Argument(
        None,
        help="Just command and arguments to run (e.g., 'lint', 'test -v'). If not provided, runs 'just' without arguments to show available commands.",
    ),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available repositories",
    ),
):
    """Run just commands in a cloned repository.

    Usage:
        dbx just <repo_name> [just_command] [args...]

    If a just command is provided after the repo name, it will be executed.
    If no just command is provided, 'just' will be run without arguments to show available commands.

    Examples:
        dbx just mongo-python-driver          # Show available just commands
        dbx just mongo-python-driver lint     # Run 'just lint'
        dbx just mongo-python-driver test -v  # Run 'just test -v'
    """
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # just_args will be None if not provided, or a list of strings if provided
    if just_args is None:
        just_args = []

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

        typer.echo(f"Available repositories in {base_dir}:\n")
        for repo in repos:
            typer.echo(f"  [{repo['group']}] {repo['name']}")
        return

    # Require repo_name if not listing
    if not repo_name:
        typer.echo("❌ Error: Repository name is required", err=True)
        typer.echo("\nUsage: dbx just <repo_name> [just_command]")
        typer.echo("       dbx just --list")
        raise typer.Exit(1)

    # Find the repository
    repo = find_repo_by_name(repo_name, base_dir)
    if not repo:
        typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
        typer.echo("\nRun 'dbx just --list' to see available repositories")
        raise typer.Exit(1)

    repo_path = Path(repo["path"])

    # Check if justfile exists
    if not (repo_path / "justfile").exists() and not (repo_path / "Justfile").exists():
        typer.echo(f"⚠️  Warning: No justfile found in {repo_path}", err=True)
        typer.echo("This repository may not use just for task automation.", err=True)
        raise typer.Exit(1)

    # Build just command
    just_cmd = ["just"]
    if just_args:
        just_cmd.extend(just_args)
        typer.echo(f"Running 'just {' '.join(just_args)}' in {repo_path}...\n")
    else:
        typer.echo(f"Running 'just' in {repo_path}...\n")

    if verbose:
        typer.echo(f"[verbose] Running command: {' '.join(just_cmd)}")
        typer.echo(f"[verbose] Working directory: {repo_path}\n")

    # Run just in the repository
    result = subprocess.run(
        just_cmd,
        cwd=str(repo_path),
        check=False,
    )

    if result.returncode != 0:
        raise typer.Exit(result.returncode)
