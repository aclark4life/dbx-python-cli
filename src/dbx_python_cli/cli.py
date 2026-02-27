"""Main CLI entry point for dbx."""

import typer

from dbx_python_cli.commands import (
    branch,
    clone,
    config,
    docs,
    edit,
    env,
    install,
    just,
    list,
    log,
    open,
    project,
    remove,
    status,
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
app.add_typer(docs.app, name="docs")
app.add_typer(edit.app, name="edit")
app.add_typer(env.app, name="env")
app.add_typer(install.app, name="install")
app.add_typer(just.app, name="just")
app.add_typer(list.app, name="list")
app.add_typer(log.app, name="log")
app.add_typer(open.app, name="open")
app.add_typer(project.app, name="project")
app.add_typer(remove.app, name="remove")
app.add_typer(status.app, name="status")
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
):
    """A command line tool for DBX Python development tasks. AI first. De-siloing happens here. Go from 'zero to hero' in just a few minutes."""
    # Store verbose flag in context for subcommands to access
    ctx.obj = {"verbose": verbose}


if __name__ == "__main__":
    app()
