"""Configuration management commands."""

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
