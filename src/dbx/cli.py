"""Main CLI entry point for dbx."""

import click


@click.group()
@click.version_option(version="0.1.0", prog_name="dbx")
def main():
    """dbx - A command line interface tool."""
    pass


if __name__ == "__main__":
    main()

