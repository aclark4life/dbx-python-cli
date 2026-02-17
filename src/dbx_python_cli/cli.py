"""Main CLI entry point for dbx."""

import typer

from dbx_python_cli.commands import (
    branch,
    clone,
    config,
    env,
    fetch,
    install,
    just,
    log,
    open,
    project,
    remote,
    remove,
    switch,
    sync,
    test,
)

app = typer.Typer(
    help="A command line tool for DBX Python development tasks. AI first. De-siloing happens here.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)

# Add subcommands (alphabetically sorted)
app.add_typer(branch.app, name="branch")
app.add_typer(clone.app, name="clone")
app.add_typer(config.app, name="config")
app.add_typer(env.app, name="env")
app.add_typer(fetch.app, name="fetch")
app.add_typer(install.app, name="install")
app.add_typer(just.app, name="just")
app.add_typer(log.app, name="log")
app.add_typer(open.app, name="open")
app.add_typer(project.app, name="project")
app.add_typer(remote.app, name="remote")
app.add_typer(remove.app, name="remove")
app.add_typer(switch.app, name="switch")
app.add_typer(sync.app, name="sync")
app.add_typer(test.app, name="test")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo("dbx, version 0.1.0")
        raise typer.Exit()


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
    from dbx_python_cli.commands import repo_utils as repo

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
            typer.echo("\nClone repositories using: dbx clone -g <group>")
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
