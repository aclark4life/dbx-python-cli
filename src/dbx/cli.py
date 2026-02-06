"""Main CLI entry point for dbx."""

import typer

app = typer.Typer(help="dbx - A command line interface tool.")


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
    )
):
    """dbx - A command line interface tool."""
    pass


if __name__ == "__main__":
    app()

