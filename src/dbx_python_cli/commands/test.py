"""Test command for running pytest in repositories."""

import subprocess
from pathlib import Path
from typing import Optional

import typer

from dbx_python_cli.commands.repo import (
    find_repo_by_name,
    get_base_dir,
    get_config,
    get_test_runner,
)
from dbx_python_cli.commands.venv_utils import get_venv_info

app = typer.Typer(
    help="Test commands",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": False,
    },
    no_args_is_help=True,
)


@app.callback(
    invoke_without_command=True, context_settings={"allow_interspersed_args": False}
)
def test_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to test"),
    test_args: list[str] = typer.Argument(
        None,
        help="Additional arguments to pass to the test runner (e.g., '--verbose', '-k test_name'). For pytest, these are passed directly. For custom test runners, all args are forwarded.",
    ),
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
        help="Only run tests matching the given keyword expression (passed to pytest -k). Note: Use test_args for custom test runners.",
    ),
    group: Optional[str] = typer.Option(
        None,
        "--group",
        "-g",
        help="Group name to use for venv (e.g., 'pymongo')",
    ),
):
    """Run tests in a cloned repository.

    Usage:
        dbx test <repo_name> [test_args...]
        dbx test <repo_name> -k <keyword>
        dbx test <repo_name> -g <group>

    Examples:
        dbx test mongo-python-driver                    # Run pytest
        dbx test mongo-python-driver -v                 # Run pytest with verbose
        dbx test mongo-python-driver -k test_insert     # Run specific test
        dbx test django --verbose                       # Run custom test runner with args
    """
    # If a subcommand was invoked, don't run this logic
    if ctx.invoked_subcommand is not None:
        return

    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # test_args will be None if not provided, or a list of strings if provided
    if test_args is None:
        test_args = []

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Config: {config}\n")

        # List repos if requested
        if list_repos:
            from dbx_python_cli.commands.repo import list_repos as list_repos_func

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
                typer.echo("Run 'dbx clone -g <group>' to clone repositories first.")
            raise typer.Exit(0)

        # Require repo_name if not listing
        if not repo_name:
            typer.echo("❌ Error: Repository name is required", err=True)
            typer.echo("\nUsage: dbx test <repo_name> [OPTIONS]")
            typer.echo("   or: dbx test --list")
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

        # Get test runner configuration
        test_runner = get_test_runner(config, repo["group"], repo_name)

        # Build test command
        if test_runner:
            # Use custom test runner (relative path from repo root)
            test_script = repo_path / test_runner
            if not test_script.exists():
                typer.echo(f"❌ Error: Test runner not found: {test_script}", err=True)
                raise typer.Exit(1)

            test_cmd = [python_path, str(test_script)]

            # Add test_args if provided
            if test_args:
                test_cmd.extend(test_args)
                typer.echo(
                    f"Running {test_runner} {' '.join(test_args)} in {repo_path}..."
                )
            else:
                typer.echo(f"Running {test_runner} in {repo_path}...")

            # Warn if -k/--keyword option is used with custom test runner
            if keyword:
                typer.echo(
                    "⚠️  Warning: -k/--keyword option not supported with custom test runner. Use test_args instead.",
                    err=True,
                )
        else:
            # Use default pytest
            test_cmd = [python_path, "-m", "pytest"]

            # Add test_args if provided
            if test_args:
                test_cmd.extend(test_args)

            # Add verbose flag if set
            if verbose and "-v" not in test_args and "--verbose" not in test_args:
                test_cmd.append("-v")

            # Add keyword filter if set
            if keyword:
                test_cmd.extend(["-k", keyword])
                typer.echo(f"Running pytest -k '{keyword}' in {repo_path}...")
            elif test_args:
                typer.echo(f"Running pytest {' '.join(test_args)} in {repo_path}...")
            else:
                typer.echo(f"Running pytest in {repo_path}...")

        if venv_type == "group":
            typer.echo(f"Using group venv: {group_path}/.venv\n")
        elif venv_type == "venv":
            typer.echo(f"Using venv: {python_path}\n")
        else:
            typer.echo(f"⚠️  No venv found, using system Python: {python_path}\n")

        if verbose:
            typer.echo(f"[verbose] Running command: {' '.join(test_cmd)}")
            typer.echo(f"[verbose] Working directory: {repo_path}\n")

        # Run test command in the repository
        result = subprocess.run(
            test_cmd,
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
