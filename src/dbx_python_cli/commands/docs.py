"""Docs command for opening the project documentation."""

import webbrowser

import typer

DOCS_URL = "https://dbx-python-cli.readthedocs.io/"

app = typer.Typer(
    help="Open the dbx documentation in a web browser",
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def docs_callback():
    """Open the dbx documentation on Read the Docs."""
    typer.echo(f"📖 Opening docs: {DOCS_URL}")
    webbrowser.open(DOCS_URL)
