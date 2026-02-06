"""Main CLI entry point for dbx."""

import typer

from dbx_python_cli.commands import repo

app = typer.Typer(
    help="A command line tool for DBX Python development tasks. AI first. De-siloing happens here.",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Add subcommands
app.add_typer(repo.app, name="repo")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo("dbx, version 0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    """A command line tool for DBX Python development tasks. AI first. De-siloing happens here."""
    pass


if __name__ == "__main__":
    app()
