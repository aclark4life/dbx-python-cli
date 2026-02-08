"""Main CLI entry point for dbx."""

import typer

from dbx_python_cli.commands import env, install, just, project, repo, test

app = typer.Typer(
    help="A command line tool for DBX Python development tasks. AI first. De-siloing happens here.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)

# Add subcommands
app.add_typer(repo.app, name="repo")
app.add_typer(env.app, name="env")
app.add_typer(test.app, name="test")
app.add_typer(install.app, name="install")
app.add_typer(just.app, name="just")
app.add_typer(project.app, name="project")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo("dbx, version 0.1.0")
        raise typer.Exit()


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
    user_config_path = repo.get_config_path()
    default_config_path = repo.get_default_config_path()

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


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show more detailed output.",
    ),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Show repository status (cloned vs available)",
    ),
):
    """A command line tool for DBX Python development tasks. AI first. De-siloing happens here."""
    # Store verbose flag in context for subcommands to access
    ctx.obj = {"verbose": verbose}

    # Handle list repos flag
    if list_repos:
        from dbx_python_cli.commands.repo_utils import list_repos as format_repos

        config = repo.get_config()
        base_dir = repo.get_base_dir(config)

        formatted_output = format_repos(base_dir, config=config)

        if not formatted_output:
            typer.echo(f"Base directory: {base_dir}\n")
            typer.echo("No repositories found.")
            typer.echo("\nClone repositories using: dbx repo clone -g <group>")
            raise typer.Exit(0)

        typer.echo(f"Base directory: {base_dir}\n")
        typer.echo("Repository status:\n")
        typer.echo(formatted_output)
        typer.echo(
            "\nLegend: ✓ = cloned, ○ = available to clone, ? = cloned but not in config"
        )
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
