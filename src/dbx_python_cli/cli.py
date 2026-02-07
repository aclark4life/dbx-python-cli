"""Main CLI entry point for dbx."""

import typer

from dbx_python_cli.commands import install, just, repo, test

app = typer.Typer(
    help="A command line tool for DBX Python development tasks. AI first. De-siloing happens here.",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Add subcommands
app.add_typer(repo.app, name="repo")
app.add_typer(test.app, name="test")
app.add_typer(install.app, name="install")
app.add_typer(just.app, name="just")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo("dbx, version 0.1.0")
        raise typer.Exit()


@app.callback()
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
    """A command line tool for DBX Python development tasks. AI first. De-siloing happens here."""
    # Store verbose flag in context for subcommands to access
    ctx.obj = {"verbose": verbose}


if __name__ == "__main__":
    app()
