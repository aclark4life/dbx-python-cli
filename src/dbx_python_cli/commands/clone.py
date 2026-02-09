"""Clone command for cloning repositories."""

import subprocess

import typer

from dbx_python_cli.commands import repo

app = typer.Typer(
    help="Clone repositories",
    no_args_is_help=True,
    invoke_without_command=True,
    context_settings={
        "allow_interspersed_args": False,
        "help_option_names": ["-h", "--help"],
    },
)


@app.callback()
def clone_callback(
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
