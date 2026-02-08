"""Repository management commands."""

import subprocess
import tomllib
from pathlib import Path

import typer

app = typer.Typer(
    help="Repository management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def repo_callback(
    ctx: typer.Context,
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="Show repository status (cloned vs available)",
    ),
):
    """Repository management commands."""
    if list_repos:
        from dbx_python_cli.commands.repo_utils import list_repos as format_repos

        config = get_config()
        base_dir = get_base_dir(config)

        formatted_output = format_repos(base_dir, config=config)

        if not formatted_output:
            typer.echo("No repositories found.")
            typer.echo(f"\nBase directory: {base_dir}")
            typer.echo("\nClone repositories using: dbx repo clone -g <group>")
            raise typer.Exit(0)

        typer.echo("Repository status:\n")
        typer.echo(formatted_output)
        typer.echo(
            "\nLegend: ✓ = cloned, ○ = available to clone, ? = cloned but not in config"
        )

        typer.echo(f"\nBase directory: {base_dir}")
        raise typer.Exit(0)


def get_config_path():
    """Get the path to the user config file."""
    config_dir = Path.home() / ".config" / "dbx-python-cli"
    return config_dir / "config.toml"


def get_default_config_path():
    """Get the path to the default config file shipped with the package."""
    return Path(__file__).parent.parent / "config.toml"


def get_config():
    """Load configuration from user config or default config."""
    user_config_path = get_config_path()
    default_config_path = get_default_config_path()

    # Try user config first
    if user_config_path.exists():
        with open(user_config_path, "rb") as f:
            return tomllib.load(f)

    # Fall back to default config
    if default_config_path.exists():
        with open(default_config_path, "rb") as f:
            return tomllib.load(f)

    # If neither exists, return empty config
    return {}


def get_base_dir(config):
    """Get the base directory for cloning repos."""
    base_dir = config.get("repo", {}).get("base_dir", "~/repos")
    return Path(base_dir).expanduser()


def get_repo_groups(config):
    """Get repository groups from config."""
    return config.get("repo", {}).get("groups", {})


def get_install_dirs(config, group_name, repo_name):
    """
    Get install directories for a repository.

    For monorepos, returns a list of subdirectories to install.
    For regular repos, returns None (install from root).

    Args:
        config: Configuration dictionary
        group_name: Name of the group (e.g., 'langchain')
        repo_name: Name of the repository (e.g., 'langchain-mongodb')

    Returns:
        list: List of install directories, or None if not a monorepo
    """
    groups = get_repo_groups(config)
    if group_name not in groups:
        return None

    install_dirs_config = groups[group_name].get("install_dirs", {})
    return install_dirs_config.get(repo_name)


@app.command()
def clone(
    ctx: typer.Context,
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
    """Clone repositories from a specified group."""
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        groups = get_repo_groups(config)

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

        # Require group if not listing
        if not group:
            typer.echo("❌ Error: Group name required", err=True)
            typer.echo("\nUsage: dbx repo clone -g <group>")
            typer.echo("   or: dbx repo clone --list")
            raise typer.Exit(1)

        if group not in groups:
            typer.echo(f"Error: Group '{group}' not found in configuration.", err=True)
            typer.echo(f"Available groups: {', '.join(groups.keys())}", err=True)
            raise typer.Exit(1)

        repos = groups[group].get("repos", [])
        if not repos:
            typer.echo(f"Error: No repositories defined for group '{group}'.", err=True)
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

        if fork_user:
            typer.echo(
                f"Cloning {len(repos)} repository(ies) from {fork_user}'s forks to {group_dir}"
            )
        else:
            typer.echo(
                f"Cloning {len(repos)} repository(ies) from group '{group}' to {group_dir}"
            )

        for repo_url in repos:
            # Extract repo name from URL
            repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
            repo_path = group_dir / repo_name

            if repo_path.exists():
                typer.echo(f"  ⏭️  {repo_name} (already exists)")
            else:
                # Determine clone URL (fork or upstream)
                clone_url = repo_url
                upstream_url = repo_url

                if fork_user:
                    # Replace the org/user in the URL with the fork user
                    # Handle both SSH and HTTPS URLs
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
        config = get_config()
        base_dir = get_base_dir(config)
        groups = get_repo_groups(config)

        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Available groups: {list(groups.keys())}\n")

        # Handle --list flag
        if list_repos:
            from dbx_python_cli.commands.repo_utils import list_repos as format_repos

            formatted_output = format_repos(base_dir, config=config)
            if not formatted_output:
                typer.echo("No repositories found.")
                typer.echo("\nClone repositories using: dbx repo clone -g <group>")
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
                typer.echo(f"\nClone repositories using: dbx repo clone -g {group}")
                raise typer.Exit(1)

            typer.echo(
                f"Syncing {len(group_repos)} repository(ies) in group '{group}':\n"
            )

            for repo in group_repos:
                _sync_repository(repo["path"], repo["name"], verbose, force)

            typer.echo(f"\n✨ Done! Synced {len(group_repos)} repository(ies)")
            return

        # Handle single repo sync
        if not repo_name:
            typer.echo("❌ Error: Repository name or group required", err=True)
            typer.echo("\nUsage: dbx repo sync <repo-name>")
            typer.echo("   or: dbx repo sync -g <group>")
            typer.echo("   or: dbx repo sync --list")
            raise typer.Exit(1)

        # Find the repository
        repo = find_repo_by_name(repo_name, base_dir)
        if not repo:
            typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
            typer.echo("\nUse 'dbx repo sync --list' to see available repositories")
            raise typer.Exit(1)

        _sync_repository(repo["path"], repo["name"], verbose, force)

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
                f"  ⚠️  {repo_name}: Not on a branch (detached HEAD state)",
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
            f"     Try running: dbx repo sync {repo_name} --force",
            err=True,
        )
