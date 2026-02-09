"""Configuration management commands."""

import os
import subprocess
import typer

from dbx_python_cli.commands.repo import get_config_path, get_default_config_path

app = typer.Typer(
    help="Configuration management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def init(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt and overwrite existing config",
    ),
):
    """Initialize user configuration file."""
    user_config_path = get_config_path()
    default_config_path = get_default_config_path()

    if user_config_path.exists():
        typer.echo(f"Configuration file already exists at {user_config_path}")
        if not yes:
            overwrite = typer.confirm("Do you want to overwrite it?")
            if not overwrite:
                typer.echo("Aborted.")
                raise typer.Exit(0)

    # Create config directory if it doesn't exist
    user_config_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy default config to user config
    if default_config_path.exists():
        import shutil

        shutil.copy(default_config_path, user_config_path)
        typer.echo(f"✅ Configuration file created at {user_config_path}")
        typer.echo("\nYou can now edit this file to customize your repository groups.")
    else:
        typer.echo(
            f"Error: Default configuration not found at {default_config_path}",
            err=True,
        )
        raise typer.Exit(1)


@app.command()
def edit():
    """Edit the configuration file with your default editor.

    Opens the configuration file using the editor specified in the EDITOR
    environment variable. If EDITOR is not set, falls back to common editors
    (vim, nano, vi) or uses 'open' on macOS.

    Examples:
        dbx config edit                    # Open with default editor
        EDITOR=code dbx config edit        # Open with VS Code
        EDITOR=nano dbx config edit        # Open with nano
    """
    config_path = get_config_path()

    if not config_path.exists():
        typer.echo(f"❌ Configuration file not found at {config_path}", err=True)
        typer.echo("\nCreate it first using: dbx config init")
        raise typer.Exit(1)

    # Get editor from environment variable
    editor = os.environ.get("EDITOR")

    if not editor:
        # Try common editors in order of preference
        common_editors = ["vim", "nano", "vi"]
        for candidate in common_editors:
            try:
                # Check if editor exists in PATH
                subprocess.run(
                    ["which", candidate],
                    check=True,
                    capture_output=True,
                )
                editor = candidate
                break
            except subprocess.CalledProcessError:
                continue

        # If no common editor found, try 'open' on macOS
        if not editor:
            import platform
            if platform.system() == "Darwin":
                editor = "open"
            else:
                typer.echo(
                    "❌ No editor found. Please set the EDITOR environment variable.",
                    err=True,
                )
                typer.echo("\nExample: export EDITOR=nano")
                raise typer.Exit(1)

    typer.echo(f"📝 Opening {config_path} with {editor}...")

    try:
        # Open the editor
        result = subprocess.run([editor, str(config_path)])

        if result.returncode == 0:
            typer.echo("✅ Configuration file saved")
        else:
            typer.echo(
                f"⚠️  Editor exited with code {result.returncode}",
                err=True,
            )
            raise typer.Exit(result.returncode)
    except FileNotFoundError:
        typer.echo(
            f"❌ Editor '{editor}' not found. Please check your EDITOR environment variable.",
            err=True,
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        typer.echo("\n⚠️  Editing cancelled")
        raise typer.Exit(130)
