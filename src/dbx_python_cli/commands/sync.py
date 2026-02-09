"""Sync command for syncing repositories with upstream."""

import subprocess
from pathlib import Path

import typer

from dbx_python_cli.commands import repo

app = typer.Typer(
    help="Sync repositories with upstream",
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "allow_interspersed_args": False,
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def sync_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(
        None,
        help="Repository name to sync (e.g., mongo-python-driver)",
    ),
    group: str = typer.Option(
        None,
        "--group",
        "-g",
        help="Sync all repositories in a group",
    ),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Show repository status (cloned vs available)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force push after rebasing (use if previous sync failed)",
    ),
):
    """Sync repository with upstream by fetching, rebasing, and pushing."""
    from dbx_python_cli.commands.repo_utils import find_all_repos, find_repo_by_name

    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = repo.get_config()
        base_dir = repo.get_base_dir(config)
        groups = repo.get_repo_groups(config)

        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Available groups: {list(groups.keys())}\n")

        # Handle --list flag
        if list_repos:
            from dbx_python_cli.commands.repo_utils import list_repos as format_repos

            formatted_output = format_repos(base_dir, config=config)
            if not formatted_output:
                typer.echo("No repositories found.")
                typer.echo("\nClone repositories using: dbx clone -g <group>")
                return

            typer.echo(f"Repository status in {base_dir}:\n")
            typer.echo(formatted_output)
            typer.echo(
                "\nLegend: ✓ = cloned, ○ = available to clone, ? = cloned but not in config"
            )
            return

        # Handle group sync
        if group:
            if group not in groups:
                typer.echo(
                    f"❌ Error: Group '{group}' not found in configuration.", err=True
                )
                typer.echo(f"Available groups: {', '.join(groups.keys())}", err=True)
                raise typer.Exit(1)

            # Find all repos in the group
            all_repos = find_all_repos(base_dir)
            group_repos = [r for r in all_repos if r["group"] == group]

            if not group_repos:
                typer.echo(
                    f"❌ Error: No repositories found for group '{group}'.", err=True
                )
                typer.echo(f"\nClone repositories using: dbx clone -g {group}")
                raise typer.Exit(1)

            typer.echo(
                f"Syncing {len(group_repos)} repository(ies) in group '{group}':\n"
            )

            for repo_info in group_repos:
                _sync_repository(repo_info["path"], repo_info["name"], verbose, force)

            typer.echo(f"\n✨ Done! Synced {len(group_repos)} repository(ies)")
            return

        # Handle single repo sync
        if not repo_name:
            typer.echo("❌ Error: Repository name or group required", err=True)
            typer.echo("\nUsage: dbx sync <repo-name>")
            typer.echo("   or: dbx sync -g <group>")
            typer.echo("   or: dbx sync --list")
            raise typer.Exit(1)

        # Find the repository
        repo_info = find_repo_by_name(repo_name, base_dir)
        if not repo_info:
            typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
            typer.echo("\nUse 'dbx sync --list' to see available repositories")
            raise typer.Exit(1)

        _sync_repository(repo_info["path"], repo_info["name"], verbose, force)

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


def _sync_repository(
    repo_path: Path, repo_name: str, verbose: bool = False, force: bool = False
):
    """Sync a single repository with upstream."""
    typer.echo(f"  🔄 Syncing {repo_name}...")

    if verbose:
        typer.echo(f"  [verbose] Repository path: {repo_path}")
        if force:
            typer.echo("  [verbose] Force push enabled")

    # Check if upstream remote exists
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "remote"],
            check=True,
            capture_output=True,
            text=True,
        )
        remotes = result.stdout.strip().split("\n")

        if "upstream" not in remotes:
            typer.echo(
                f"  ⚠️  {repo_name}: No 'upstream' remote found (skipping)",
                err=True,
            )
            return

    except subprocess.CalledProcessError as e:
        typer.echo(
            f"  ❌ {repo_name}: Failed to check remotes: {e.stderr}",
            err=True,
        )
        return

    # Get current branch
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        )
        current_branch = result.stdout.strip()

        if not current_branch:
            typer.echo(
                f"  ⚠️  {repo_name}: Not on a branch (detached HEAD), skipping",
                err=True,
            )
            return

        if verbose:
            typer.echo(f"  [verbose] Current branch: {current_branch}")

    except subprocess.CalledProcessError as e:
        typer.echo(
            f"  ❌ {repo_name}: Failed to get current branch: {e.stderr}",
            err=True,
        )
        return

    # Fetch from upstream
    try:
        if verbose:
            typer.echo("  [verbose] Fetching from upstream...")

        subprocess.run(
            ["git", "-C", str(repo_path), "fetch", "upstream"],
            check=True,
            capture_output=not verbose,
            text=True,
        )

    except subprocess.CalledProcessError as e:
        typer.echo(
            f"  ❌ {repo_name}: Failed to fetch from upstream: {e.stderr if not verbose else ''}",
            err=True,
        )
        return

    # Rebase on upstream/<current_branch>
    try:
        if verbose:
            typer.echo(f"  [verbose] Rebasing on upstream/{current_branch}...")

        subprocess.run(
            ["git", "-C", str(repo_path), "rebase", f"upstream/{current_branch}"],
            check=True,
            capture_output=not verbose,
            text=True,
        )

    except subprocess.CalledProcessError as e:
        typer.echo(
            f"  ❌ {repo_name}: Failed to rebase on upstream/{current_branch}",
            err=True,
        )
        if not verbose and e.stderr:
            typer.echo(f"     {e.stderr.strip()}", err=True)
        typer.echo(
            f"     You may need to resolve conflicts manually in {repo_path}",
            err=True,
        )
        return

    # Push to origin
    try:
        if verbose:
            push_type = "force pushing" if force else "pushing"
            typer.echo(
                f"  [verbose] {push_type.capitalize()} to origin/{current_branch}..."
            )

        push_cmd = ["git", "-C", str(repo_path), "push"]
        if force:
            push_cmd.append("--force-with-lease")
        push_cmd.extend(["origin", current_branch])

        subprocess.run(
            push_cmd,
            check=True,
            capture_output=not verbose,
            text=True,
        )

        typer.echo(f"  ✅ {repo_name} synced and pushed successfully")

    except subprocess.CalledProcessError as e:
        typer.echo(
            f"  ⚠️  {repo_name}: Synced but failed to push to origin/{current_branch}",
            err=True,
        )
        if not verbose and e.stderr:
            typer.echo(f"     {e.stderr.strip()}", err=True)
        typer.echo(
            f"     Try running: dbx sync {repo_name} --force",
            err=True,
        )

