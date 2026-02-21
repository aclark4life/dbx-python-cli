"""Edit command for opening repositories in an editor."""

import os
import subprocess
from pathlib import Path

import typer

from dbx_python_cli.commands.repo_utils import (
    find_repo_by_name,
    get_base_dir,
    get_config,
)

# Create a Typer app that will act as a single command
app = typer.Typer(
    help="Open repositories in editor",
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "allow_interspersed_args": False,
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def edit_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to open in editor"),
):
    """Open a repository in your editor.

    Uses the EDITOR environment variable to determine which editor to use.
    Falls back to 'vim' if EDITOR is not set.

    Usage::

        dbx edit <repo_name>

    Examples::

        dbx edit mongo-python-driver    # Open repo in editor
        dbx edit --list                 # List available repos
    """
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Config: {config}\n")

        # Require repo_name
        if not repo_name:
            typer.echo("❌ Error: Repository name is required", err=True)
            typer.echo("\nUsage: dbx edit <repo_name>")
            raise typer.Exit(1)

        # Find the repository
        repo = find_repo_by_name(repo_name, base_dir)
        if not repo:
            typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
            typer.echo("\nRun 'dbx list' to see available repositories")
            raise typer.Exit(1)

        repo_path = Path(repo["path"])

        # Get the editor from environment variable, default to vim
        editor = os.environ.get("EDITOR", "vim")

        if verbose:
            typer.echo(f"[verbose] Repository path: {repo_path}")
            typer.echo(f"[verbose] Editor: {editor}")

        typer.echo(f"📝 Opening {repo_name} in {editor}...")

        # Open the editor with the repository directory
        try:
            subprocess.run([editor, str(repo_path)], check=True)
            typer.echo(f"✨ Closed {editor}")
        except subprocess.CalledProcessError as e:
            typer.echo(f"❌ Error: Failed to open editor: {e}", err=True)
            raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo(
                f"❌ Error: Editor '{editor}' not found. Please set the EDITOR environment variable.",
                err=True,
            )
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
