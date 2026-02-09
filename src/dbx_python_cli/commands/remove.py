"""Remove command for removing repository groups."""

import shutil

import typer

from dbx_python_cli.commands import repo

app = typer.Typer(
    help="Remove repository groups",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def remove_callback(
    ctx: typer.Context,
    group_name: str = typer.Argument(
        None,
        help="Repository group to remove (e.g., pymongo, langchain)",
    ),
    list_groups: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List available groups",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
):
    """Remove a repository group directory.

    Examples:
        dbx remove pymongo          # Remove the pymongo group directory
        dbx remove langchain -f     # Remove without confirmation
        dbx remove --list           # List available groups
    """
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = repo.get_config()
        base_dir = repo.get_base_dir(config)
        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Config: {config}\n")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

    # Handle --list flag
    if list_groups:
        groups = repo.get_repo_groups(config)
        if not groups:
            typer.echo("No groups found in configuration.")
            return

        typer.echo("Available groups:\n")
        for group_name_item in groups.keys():
            group_dir = base_dir / group_name_item
            if group_dir.exists():
                typer.echo(f"  ✓ {group_name_item} (cloned)")
            else:
                typer.echo(f"  ○ {group_name_item} (not cloned)")
        return

    # Require group_name if not listing
    if not group_name:
        typer.echo("❌ Error: Group name is required", err=True)
        typer.echo("\nUsage: dbx remove <group_name>")
        typer.echo("       dbx remove --list")
        raise typer.Exit(1)

    # Check if group directory exists
    group_dir = base_dir / group_name
    if not group_dir.exists():
        typer.echo(
            f"❌ Error: Group directory '{group_name}' not found at {group_dir}",
            err=True,
        )
        typer.echo("\nRun 'dbx remove --list' to see available groups")
        raise typer.Exit(1)

    # Check if it's a directory
    if not group_dir.is_dir():
        typer.echo(f"❌ Error: '{group_dir}' is not a directory", err=True)
        raise typer.Exit(1)

    # Count repositories in the group
    from dbx_python_cli.commands.repo_utils import find_all_repos

    repos = find_all_repos(base_dir)
    group_repos = [r for r in repos if r["group"] == group_name]
    repo_count = len(group_repos)

    # Show what will be removed
    typer.echo(f"📁 Group directory: {group_dir}")
    if repo_count > 0:
        typer.echo(f"📦 Repositories to remove: {repo_count}")
        if verbose:
            for repo_info in group_repos:
                typer.echo(f"   - {repo_info['name']}")
    else:
        typer.echo("📦 No repositories found in this group")

    # Confirm removal unless --force is used
    if not force:
        typer.echo()
        confirm = typer.confirm(
            f"⚠️  Are you sure you want to remove the '{group_name}' group directory?",
            default=False,
        )
        if not confirm:
            typer.echo("❌ Removal cancelled")
            raise typer.Exit(0)

    # Remove the directory
    try:
        if verbose:
            typer.echo(f"\n[verbose] Removing directory: {group_dir}")

        shutil.rmtree(group_dir)
        typer.echo(f"\n✅ Successfully removed '{group_name}' group directory")

        if repo_count > 0:
            typer.echo(f"   Removed {repo_count} repository(ies)")
    except Exception as e:
        typer.echo(f"\n❌ Failed to remove directory: {e}", err=True)
        raise typer.Exit(1)

