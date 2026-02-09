"""Main CLI entry point for dbx."""

import shutil
import subprocess
from pathlib import Path

import typer

from dbx_python_cli.commands import (
    branch,
    config,
    env,
    install,
    just,
    open,
    project,
    repo,
    switch,
    test,
)

app = typer.Typer(
    help="A command line tool for DBX Python development tasks. AI first. De-siloing happens here.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)

# Add subcommands
app.add_typer(config.app, name="config")
app.add_typer(env.app, name="env")
app.add_typer(test.app, name="test")
app.add_typer(install.app, name="install")
app.add_typer(just.app, name="just")
app.add_typer(branch.app, name="branch")
app.add_typer(switch.app, name="switch")
app.add_typer(open.app, name="open")
app.add_typer(project.app, name="project")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo("dbx, version 0.1.0")
        raise typer.Exit()


@app.command()
def clone(
    ctx: typer.Context,
    repo_name: str = typer.Argument(
        None,
        help="Repository name to clone (e.g., django-mongodb-backend)",
    ),
    group: str = typer.Option(
        None,
        "--group",
        "-g",
        help="Repository group to clone (e.g., pymongo, langchain, django)",
    ),
    list_groups: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List available groups",
    ),
    fork: str = typer.Option(
        None,
        "--fork",
        help="Clone from your fork instead of upstream (provide GitHub username, or use config default if no value given)",
    ),
):
    """Clone a repository by name or all repositories from a group."""
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
        if list_groups:
            if not groups:
                typer.echo("No groups found in configuration.")
                return

            typer.echo("Available groups:\n")
            for group_name, group_config in sorted(groups.items()):
                repo_count = len(group_config.get("repos", []))
                typer.echo(f"  • {group_name} ({repo_count} repositories)")
            return

        # Handle individual repo clone
        if repo_name:
            # Find the repo in all groups
            found_repo = None
            found_group = None

            for group_name, group_config in groups.items():
                for repo_url in group_config.get("repos", []):
                    # Extract repo name from URL
                    url_repo_name = repo_url.split("/")[-1].replace(".git", "")
                    if url_repo_name == repo_name:
                        found_repo = repo_url
                        found_group = group_name
                        break
                if found_repo:
                    break

            if not found_repo:
                typer.echo(
                    f"❌ Error: Repository '{repo_name}' not found in any group.",
                    err=True,
                )
                typer.echo(
                    "\nUse 'dbx clone --list' to see available groups and repositories"
                )
                raise typer.Exit(1)

            # Clone single repo
            repos = [found_repo]
            group = found_group

            if verbose:
                typer.echo(f"[verbose] Found '{repo_name}' in group '{group}'")

        # Handle group clone
        elif group:
            # Get repositories for the group
            if group not in groups:
                typer.echo(
                    f"❌ Error: Group '{group}' not found in configuration.", err=True
                )
                typer.echo(f"Available groups: {', '.join(groups.keys())}", err=True)
                raise typer.Exit(1)

            repos = groups[group].get("repos", [])
            if not repos:
                typer.echo(
                    f"❌ Error: No repositories found in group '{group}'.", err=True
                )
                raise typer.Exit(1)

        else:
            typer.echo("❌ Error: Repository name or group required", err=True)
            typer.echo("\nUsage: dbx clone <repo-name>")
            typer.echo("   or: dbx clone -g <group>")
            typer.echo("   or: dbx clone --list")
            raise typer.Exit(1)

        # Handle fork flag
        fork_user = None
        if fork is not None:
            # If --fork is provided without a value, try to get from config
            if fork == "":
                fork_user = config.get("repo", {}).get("fork_user")
                if not fork_user:
                    typer.echo(
                        "❌ Error: --fork flag requires a GitHub username or set 'fork_user' in config",
                        err=True,
                    )
                    raise typer.Exit(1)
            else:
                fork_user = fork

            if verbose:
                typer.echo(f"[verbose] Using fork workflow with user: {fork_user}\n")

        # Create group directory under base directory
        group_dir = base_dir / group
        group_dir.mkdir(parents=True, exist_ok=True)

        # Display appropriate message
        if len(repos) == 1:
            single_repo_name = repos[0].split("/")[-1].replace(".git", "")
            if fork_user:
                typer.echo(
                    f"Cloning {single_repo_name} from {fork_user}'s fork to {group_dir}"
                )
            else:
                typer.echo(f"Cloning {single_repo_name} to {group_dir}")
        else:
            if fork_user:
                typer.echo(
                    f"Cloning {len(repos)} repository(ies) from {fork_user}'s forks to {group_dir}"
                )
            else:
                typer.echo(
                    f"Cloning {len(repos)} repository(ies) from group '{group}' to {group_dir}"
                )

        for repo_url in repos:
            # Extract repository name from URL
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            repo_path = group_dir / repo_name

            if repo_path.exists():
                typer.echo(f"  ⏭️  {repo_name} already exists, skipping")
                continue

            # Determine clone URL and upstream URL
            if fork_user:
                # Replace the org/user in the URL with the fork user
                # Handle both SSH and HTTPS URLs
                clone_url = repo_url
                upstream_url = repo_url

                if "git@github.com:" in repo_url:
                    # SSH format: git@github.com:org/repo.git
                    parts = repo_url.split(":")
                    if len(parts) == 2:
                        repo_part = parts[1].split("/", 1)
                        if len(repo_part) == 2:
                            clone_url = f"git@github.com:{fork_user}/{repo_part[1]}"
                elif "github.com/" in repo_url:
                    # HTTPS format: https://github.com/org/repo.git
                    parts = repo_url.split("github.com/")
                    if len(parts) == 2:
                        repo_part = parts[1].split("/", 1)
                        if len(repo_part) == 2:
                            clone_url = (
                                f"{parts[0]}github.com/{fork_user}/{repo_part[1]}"
                            )
            else:
                clone_url = repo_url
                upstream_url = None

            typer.echo(f"  📦 Cloning {repo_name}...")
            if verbose:
                typer.echo(f"  [verbose] Clone URL: {clone_url}")
                if fork_user:
                    typer.echo(f"  [verbose] Upstream URL: {upstream_url}")
                typer.echo(f"  [verbose] Destination: {repo_path}")

            try:
                # Clone the repository
                subprocess.run(
                    ["git", "clone", clone_url, str(repo_path)],
                    check=True,
                    capture_output=not verbose,
                    text=True,
                )

                # If using fork workflow, add upstream remote
                if fork_user:
                    subprocess.run(
                        [
                            "git",
                            "-C",
                            str(repo_path),
                            "remote",
                            "add",
                            "upstream",
                            upstream_url,
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    typer.echo(
                        f"  ✅ {repo_name} cloned from fork (upstream remote added)"
                    )
                else:
                    typer.echo(f"  ✅ {repo_name} cloned successfully")

            except subprocess.CalledProcessError as e:
                typer.echo(
                    f"  ❌ Failed to clone {repo_name}: {e.stderr if not verbose else ''}",
                    err=True,
                )

        typer.echo(f"\n✨ Done! Repositories cloned to {group_dir}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def sync(
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


@app.command()
def remove(
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
