"""Clone command for cloning repositories."""

import subprocess

import typer

from dbx_python_cli.commands import repo_utils as repo

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
    group: list[str] = typer.Option(
        None,
        "--group",
        "-g",
        help="Repository group(s) to clone (e.g., pymongo, langchain, django). Can be specified multiple times or as comma-separated values.",
    ),
    list_groups: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List available groups",
    ),
    fork: bool = typer.Option(
        True,
        "--fork",
        help="Clone from your fork instead of upstream (uses fork_user from config)",
    ),
    fork_user: str = typer.Option(
        None,
        "--fork-user",
        help="GitHub username for fork (overrides --fork and config fork_user)",
    ),
):
    """Clone a repository by name or all repositories from one or more groups."""
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
            repos_to_clone = {found_group: [found_repo]}

            if verbose:
                typer.echo(f"[verbose] Found '{repo_name}' in group '{found_group}'")

        # Handle group clone (can be multiple groups)
        elif group:
            repos_to_clone = {}

            # Parse comma-separated values
            group_names = []
            for g in group:
                # Split by comma and strip whitespace
                group_names.extend(
                    [name.strip() for name in g.split(",") if name.strip()]
                )

            # Validate all groups first
            for group_name in group_names:
                if group_name not in groups:
                    typer.echo(
                        f"❌ Error: Group '{group_name}' not found in configuration.",
                        err=True,
                    )
                    typer.echo(
                        f"Available groups: {', '.join(groups.keys())}", err=True
                    )
                    raise typer.Exit(1)

                group_repos = groups[group_name].get("repos", [])
                if not group_repos:
                    typer.echo(
                        f"❌ Error: No repositories found in group '{group_name}'.",
                        err=True,
                    )
                    raise typer.Exit(1)

                repos_to_clone[group_name] = group_repos

        else:
            typer.echo("❌ Error: Repository name or group required", err=True)
            typer.echo("\nUsage: dbx clone <repo-name>")
            typer.echo("   or: dbx clone -g <group>")
            typer.echo("   or: dbx clone -g <group1> -g <group2>")
            typer.echo("   or: dbx clone -g <group1>,<group2>")
            typer.echo("   or: dbx clone --list")
            raise typer.Exit(1)

        # Handle fork options
        effective_fork_user = None
        if fork_user:
            # --fork-user takes precedence
            effective_fork_user = fork_user
        elif fork:
            # --fork flag uses config, falls back to upstream if not set
            effective_fork_user = config.get("repo", {}).get("fork_user")
            if not effective_fork_user and verbose:
                typer.echo(
                    "[verbose] --fork specified but fork_user not in config, cloning from upstream\n"
                )

        if effective_fork_user and verbose:
            typer.echo(
                f"[verbose] Using fork workflow with user: {effective_fork_user}\n"
            )

        # Process each group
        for group_name, repos in repos_to_clone.items():
            # Create group directory under base directory
            group_dir = base_dir / group_name
            group_dir.mkdir(parents=True, exist_ok=True)

            # Display appropriate message
            if len(repos) == 1:
                single_repo_name = repos[0].split("/")[-1].replace(".git", "")
                if effective_fork_user:
                    typer.echo(
                        f"Cloning {single_repo_name} from {effective_fork_user}'s fork to {group_dir}"
                    )
                else:
                    typer.echo(f"Cloning {single_repo_name} to {group_dir}")
            else:
                if effective_fork_user:
                    typer.echo(
                        f"Cloning {len(repos)} repository(ies) from {effective_fork_user}'s forks to {group_dir}"
                    )
                else:
                    typer.echo(
                        f"Cloning {len(repos)} repository(ies) from group '{group_name}' to {group_dir}"
                    )

            for repo_url in repos:
                # Extract repository name from URL
                repo_name = repo_url.split("/")[-1].replace(".git", "")
                repo_path = group_dir / repo_name

                if repo_path.exists():
                    typer.echo(f"  ⏭️  {repo_name} already exists, skipping")
                    continue

                # Determine clone URL and upstream URL
                if effective_fork_user:
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
                                clone_url = f"git@github.com:{effective_fork_user}/{repo_part[1]}"
                    elif "github.com/" in repo_url:
                        # HTTPS format: https://github.com/org/repo.git
                        parts = repo_url.split("github.com/")
                        if len(parts) == 2:
                            repo_part = parts[1].split("/", 1)
                            if len(repo_part) == 2:
                                clone_url = f"{parts[0]}github.com/{effective_fork_user}/{repo_part[1]}"
                else:
                    clone_url = repo_url
                    upstream_url = None

                typer.echo(f"  📦 Cloning {repo_name}...")
                if verbose:
                    typer.echo(f"  [verbose] Clone URL: {clone_url}")
                    if effective_fork_user:
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
                    if effective_fork_user:
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

                        # Fetch upstream to compare commits
                        try:
                            subprocess.run(
                                ["git", "-C", str(repo_path), "fetch", "upstream"],
                                check=True,
                                capture_output=True,
                                text=True,
                            )

                            # Get the default branch name from upstream
                            result = subprocess.run(
                                [
                                    "git",
                                    "-C",
                                    str(repo_path),
                                    "symbolic-ref",
                                    "refs/remotes/upstream/HEAD",
                                ],
                                capture_output=True,
                                text=True,
                            )

                            if result and result.returncode == 0:
                                upstream_branch = result.stdout.strip().split("/")[-1]
                            else:
                                # Fallback to main/master
                                upstream_branch = "main"

                            # Count commits ahead
                            result = subprocess.run(
                                [
                                    "git",
                                    "-C",
                                    str(repo_path),
                                    "rev-list",
                                    "--count",
                                    f"upstream/{upstream_branch}..HEAD",
                                ],
                                capture_output=True,
                                text=True,
                            )

                            if result and result.returncode == 0:
                                commits_ahead = int(result.stdout.strip())
                                if commits_ahead > 0:
                                    typer.echo(
                                        f"  ✅ {repo_name} cloned from fork (upstream remote added, {commits_ahead} commit{'s' if commits_ahead != 1 else ''} ahead)"
                                    )
                                else:
                                    typer.echo(
                                        f"  ✅ {repo_name} cloned from fork (upstream remote added, up to date)"
                                    )
                            else:
                                typer.echo(
                                    f"  ✅ {repo_name} cloned from fork (upstream remote added)"
                                )
                        except (subprocess.CalledProcessError, AttributeError):
                            # If fetch or comparison fails, just show basic message
                            typer.echo(
                                f"  ✅ {repo_name} cloned from fork (upstream remote added)"
                            )
                    else:
                        typer.echo(f"  ✅ {repo_name} cloned successfully")

                except subprocess.CalledProcessError as e:
                    # If fork clone failed, try falling back to upstream
                    if effective_fork_user and upstream_url:
                        if verbose:
                            typer.echo(
                                "  [verbose] Fork clone failed, falling back to upstream"
                            )
                        try:
                            subprocess.run(
                                ["git", "clone", upstream_url, str(repo_path)],
                                check=True,
                                capture_output=not verbose,
                                text=True,
                            )
                            typer.echo(
                                f"  ✅ {repo_name} cloned from upstream (fork not found)"
                            )
                        except subprocess.CalledProcessError as upstream_error:
                            typer.echo(
                                f"  ❌ Failed to clone {repo_name}: {upstream_error.stderr if not verbose else ''}",
                                err=True,
                            )
                    else:
                        typer.echo(
                            f"  ❌ Failed to clone {repo_name}: {e.stderr if not verbose else ''}",
                            err=True,
                        )

            typer.echo(f"\n✨ Done! Repositories cloned to {group_dir}")

        # Final summary message
        total_groups = len(repos_to_clone)
        if total_groups > 1:
            typer.echo(
                f"\n🎉 All done! Cloned repositories from {total_groups} groups."
            )

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
