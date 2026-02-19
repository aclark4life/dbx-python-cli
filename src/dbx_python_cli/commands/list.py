"""List command for listing repositories."""

import typer

from dbx_python_cli.commands.repo_utils import get_base_dir, get_config, list_repos

# Create a Typer app that will act as a single command
app = typer.Typer(
    help="List repositories",
    no_args_is_help=False,
    invoke_without_command=True,
    context_settings={
        "allow_interspersed_args": False,
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def list_callback(
    ctx: typer.Context,
):
    """List all repositories (cloned and available).

    Shows a tree view of all repository groups with status indicators:
    - ✓ = cloned
    - ○ = available to clone
    - ? = cloned but not in config

    Examples::

        dbx list                    # List all repositories
    """
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Config: {config}\n")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

    formatted_output = list_repos(base_dir, config=config)

    if not formatted_output:
        typer.echo(f"Base directory: {base_dir}\n")
        typer.echo("No repositories found.")
        typer.echo("\nClone repositories using: dbx clone -g <group>")
        return

    typer.echo(f"Base directory: {base_dir}\n")
    typer.echo("Repository status:\n")
    typer.echo(formatted_output)
    typer.echo(
        "\nLegend: ✓ = cloned, ○ = available to clone, ? = cloned but not in config"
    )
