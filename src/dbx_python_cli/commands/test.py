"""Test command for running pytest in repositories."""

import subprocess
from typing import Optional

import typer

from dbx_python_cli.commands.repo import get_base_dir, get_config
from dbx_python_cli.commands.repo_utils import (
    find_repo_by_name,
)
from dbx_python_cli.commands.venv_utils import get_venv_info

app = typer.Typer(
    help="Test commands",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": False,
    },
    no_args_is_help=False,
)


@app.callback(
    invoke_without_command=True, context_settings={"allow_interspersed_args": True}
)
def test_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to test"),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Show repository status (cloned vs available)",
    ),
    keyword: str = typer.Option(
        None,
        "--keyword",
        "-k",
        help="Only run tests matching the given keyword expression (passed to pytest -k)",
    ),
    group: Optional[str] = typer.Option(
        None,
        "--group",
        "-g",
        help="Group name to use for venv (e.g., 'pymongo')",
    ),
):
    """Run pytest in a cloned repository."""
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

        # List repos if requested
        if list_repos:
            from dbx_python_cli.commands.repo_utils import (
                list_repos as list_repos_func,
            )

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
                typer.echo(
                    "Run 'dbx repo clone -g <group>' to clone repositories first."
                )
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
            typer.echo("Run 'dbx test --list' to see available repositories.", err=True)
            raise typer.Exit(1)

        repo_path = repo["path"]

        # Determine which group's venv to use
        if group:
            # Use specified group's venv
            from pathlib import Path

            group_path = Path(base_dir) / group
            if not group_path.exists():
                typer.echo(
                    f"❌ Error: Group '{group}' not found in {base_dir}", err=True
                )
                raise typer.Exit(1)
        else:
            # Default to repo's own group
            group_path = repo_path.parent

        # Detect venv
        python_path, venv_type = get_venv_info(repo_path, group_path)

        if verbose:
            typer.echo(f"[verbose] Venv type: {venv_type}")
            typer.echo(f"[verbose] Python: {python_path}\n")

        # Build pytest command using venv's Python
        pytest_cmd = [python_path, "-m", "pytest"]
        if verbose:
            pytest_cmd.append("-v")  # Add pytest verbose flag
        if keyword:
            pytest_cmd.extend(["-k", keyword])
            typer.echo(f"Running pytest -k '{keyword}' in {repo_path}...")
        else:
            typer.echo(f"Running pytest in {repo_path}...")

        if venv_type == "group":
            typer.echo(f"Using group venv: {group_path}/.venv\n")
        elif venv_type == "venv":
            typer.echo(f"Using venv: {python_path}\n")
        else:
            typer.echo(f"⚠️  No venv found, using system Python: {python_path}\n")

        if verbose:
            typer.echo(f"[verbose] Running command: {' '.join(pytest_cmd)}")
            typer.echo(f"[verbose] Working directory: {repo_path}\n")

        # Run pytest in the repository
        result = subprocess.run(
            pytest_cmd,
            cwd=str(repo_path),
            check=False,
        )

        if result.returncode == 0:
            typer.echo(f"\n✅ Tests passed in {repo_name}")
        else:
            typer.echo(f"\n❌ Tests failed in {repo_name}", err=True)
            raise typer.Exit(result.returncode)

    except typer.Exit:
        # Re-raise typer.Exit to preserve the exit code
        raise
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
