"""Install command for installing dependencies in repositories."""

import subprocess
from pathlib import Path
from typing import Optional

import typer

from dbx_python_cli.commands.repo import get_base_dir, get_config, get_install_dirs
from dbx_python_cli.commands.venv_utils import get_venv_info

app = typer.Typer(
    help="Install commands",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": False,
    },
    no_args_is_help=False,
)


def find_all_repos(base_dir):
    """Find all cloned repositories in the base directory."""
    repos = []
    if not base_dir.exists():
        return repos

    # Look for repos in group subdirectories
    for group_dir in base_dir.iterdir():
        if group_dir.is_dir():
            for repo_dir in group_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / ".git").exists():
                    repos.append(
                        {
                            "name": repo_dir.name,
                            "path": repo_dir,
                            "group": group_dir.name,
                        }
                    )
    return repos


def find_repo_by_name(repo_name, base_dir):
    """Find a repository by name in the base directory."""
    all_repos = find_all_repos(base_dir)
    for repo in all_repos:
        if repo["name"] == repo_name:
            return repo
    return None


def install_package(
    repo_path,
    python_path,
    install_dir=None,
    extras=None,
    groups=None,
    verbose=False,
):
    """
    Install a package from a directory.

    Args:
        repo_path: Path to the repository root
        python_path: Path to Python executable
        install_dir: Subdirectory to install from (for monorepos), or None for root
        extras: Comma-separated extras to install
        groups: Comma-separated dependency groups to install
        verbose: Whether to show verbose output

    Returns:
        bool: True if successful, False otherwise
    """
    # Determine the working directory
    if install_dir:
        work_dir = repo_path / install_dir
        if not work_dir.exists():
            typer.echo(f"⚠️  Warning: Install directory not found: {work_dir}", err=True)
            return False
        display_path = f"{repo_path.name}/{install_dir}"
    else:
        work_dir = repo_path
        display_path = str(repo_path)

    # Build the install spec
    install_spec = "."
    if extras:
        extras_list = [e.strip() for e in extras.split(",")]
        install_spec = f".[{','.join(extras_list)}]"

    # Install the package
    install_cmd = ["uv", "pip", "install", "--python", python_path, "-e", install_spec]

    if verbose:
        typer.echo(f"[verbose] Running command: {' '.join(install_cmd)}")
        typer.echo(f"[verbose] Working directory: {work_dir}\n")

    install_result = subprocess.run(
        install_cmd,
        cwd=str(work_dir),
        check=False,
        capture_output=not verbose,
        text=True,
    )

    if install_result.returncode != 0:
        typer.echo(f"⚠️  Warning: Installation failed for {display_path}", err=True)
        if not verbose and install_result.stderr:
            typer.echo(install_result.stderr, err=True)
        return False

    if verbose and install_result.stdout:
        typer.echo(f"[verbose] Output:\n{install_result.stdout}")

    # Install dependency groups if specified
    if groups:
        groups_list = [g.strip() for g in groups.split(",")]

        for dep_group in groups_list:
            group_cmd = [
                "uv",
                "pip",
                "install",
                "--python",
                python_path,
                "--group",
                dep_group,
            ]

            if verbose:
                typer.echo(f"[verbose] Running command: {' '.join(group_cmd)}")
                typer.echo(f"[verbose] Working directory: {work_dir}\n")

            group_result = subprocess.run(
                group_cmd,
                cwd=str(work_dir),
                check=False,
                capture_output=not verbose,
                text=True,
            )

            if group_result.returncode != 0:
                typer.echo(
                    f"⚠️  Warning: Failed to install group '{dep_group}' for {display_path}",
                    err=True,
                )
                if not verbose and group_result.stderr:
                    typer.echo(group_result.stderr, err=True)
                return False

            if verbose and group_result.stdout:
                typer.echo(f"[verbose] Output:\n{group_result.stdout}")

    return True


@app.callback(
    invoke_without_command=True, context_settings={"allow_interspersed_args": True}
)
def install_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(
        None, help="Repository name to install dependencies for"
    ),
    extras: Optional[str] = typer.Option(
        None,
        "--extras",
        "-e",
        help="Comma-separated list of extras to install (e.g., 'test', 'dev', 'aws')",
    ),
    groups: Optional[str] = typer.Option(
        None,
        "--groups",
        help="Comma-separated list of dependency groups to install (e.g., 'dev', 'test')",
    ),
    group: Optional[str] = typer.Option(
        None,
        "--group",
        "-g",
        help="Group name: use group's venv, or install all repos in group if no repo specified",
    ),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available repositories",
    ),
):
    """Install dependencies in a cloned repository using uv pip install."""
    # If a subcommand was invoked, don't run this logic
    if ctx.invoked_subcommand is not None:
        return

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

    # Handle --list flag
    if list_repos:
        repos = find_all_repos(base_dir)
        if not repos:
            typer.echo("No repositories found.")
            typer.echo("\nClone repositories using: dbx repo clone -g <group>")
            return

        typer.echo("Available repositories:\n")
        for repo in repos:
            typer.echo(f"  • {repo['name']} ({repo['group']})")
        return

    # Handle installing all repos in a group when only -g is provided
    if not repo_name and group:
        # Install all repos in the specified group
        group_path = base_dir / group
        if not group_path.exists():
            typer.echo(f"❌ Error: Group '{group}' not found in {base_dir}", err=True)
            raise typer.Exit(1)

        # Find all repos in this group
        all_repos = find_all_repos(base_dir)
        group_repos = [r for r in all_repos if r["group"] == group]

        if not group_repos:
            typer.echo(f"❌ Error: No repositories found in group '{group}'", err=True)
            typer.echo(f"\nClone repositories using: dbx repo clone -g {group}")
            raise typer.Exit(1)

        typer.echo(f"Installing all repositories in group '{group}'...\n")

        # Install each repo in the group
        failed_items = []
        total_items = 0

        for repo in group_repos:
            repo_path = Path(repo["path"])
            typer.echo(f"{'='*60}")
            typer.echo(f"Installing: {repo['name']}")
            typer.echo(f"{'='*60}\n")

            # Detect venv
            python_path, venv_type = get_venv_info(repo_path, group_path)

            if verbose:
                typer.echo(f"[verbose] Venv type: {venv_type}")
                typer.echo(f"[verbose] Python: {python_path}\n")

            # Show venv info
            if venv_type == "group":
                typer.echo(f"Using group venv: {group_path}/.venv\n")
            else:
                typer.echo("⚠️  No venv found, using system Python\n")

            # Check if this repo has install_dirs (monorepo)
            install_dirs = get_install_dirs(config, group, repo["name"])

            if install_dirs:
                # Monorepo: install each directory separately
                typer.echo(
                    f"Monorepo detected: installing {len(install_dirs)} packages...\n"
                )

                for install_dir in install_dirs:
                    total_items += 1
                    typer.echo(f"  → Installing from {install_dir}...")

                    success = install_package(
                        repo_path,
                        python_path,
                        install_dir=install_dir,
                        extras=extras,
                        groups=groups,
                        verbose=verbose,
                    )

                    if success:
                        typer.echo(f"  ✅ {install_dir} installed successfully\n")
                    else:
                        failed_items.append(f"{repo['name']}/{install_dir}")
            else:
                # Regular repo: install from root
                total_items += 1

                success = install_package(
                    repo_path,
                    python_path,
                    install_dir=None,
                    extras=extras,
                    groups=groups,
                    verbose=verbose,
                )

                if success:
                    typer.echo(f"✅ {repo['name']} installed successfully\n")
                else:
                    failed_items.append(repo["name"])

        # Summary
        typer.echo(f"\n{'='*60}")
        typer.echo("Installation Summary")
        typer.echo(f"{'='*60}")
        typer.echo(f"Total packages: {total_items}")
        typer.echo(f"Successful: {total_items - len(failed_items)}")
        if failed_items:
            typer.echo(f"Failed: {len(failed_items)}")
            typer.echo("\nFailed packages:")
            for item_name in failed_items:
                typer.echo(f"  • {item_name}")
            raise typer.Exit(1)
        else:
            typer.echo(f"\n✅ All packages in group '{group}' installed successfully!")
        return

    # Require repo_name if not listing and not installing group
    if not repo_name:
        typer.echo("❌ Error: Repository name is required", err=True)
        typer.echo("\nUsage: dbx install <repo_name> [OPTIONS]")
        typer.echo(
            "       dbx install -g <group> [OPTIONS]  # Install all repos in group"
        )
        typer.echo("       dbx install --list")
        raise typer.Exit(1)

    # Find the repository
    repo = find_repo_by_name(repo_name, base_dir)
    if not repo:
        typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
        typer.echo("\nRun 'dbx install --list' to see available repositories")
        raise typer.Exit(1)

    repo_path = Path(repo["path"])

    # Determine which group's venv to use
    if group:
        # Use specified group's venv
        group_path = base_dir / group
        if not group_path.exists():
            typer.echo(f"❌ Error: Group '{group}' not found in {base_dir}", err=True)
            raise typer.Exit(1)
    else:
        # Default to repo's own group
        group_path = repo_path.parent

    # Detect venv
    python_path, venv_type = get_venv_info(repo_path, group_path)

    if verbose:
        typer.echo(f"[verbose] Venv type: {venv_type}")
        typer.echo(f"[verbose] Python: {python_path}\n")

    # Build the install command
    install_spec = "."

    # Add extras if specified
    if extras:
        extras_list = [e.strip() for e in extras.split(",")]
        install_spec = f".[{','.join(extras_list)}]"

    # Install the package with extras
    typer.echo(f"Installing dependencies in {repo_path}...")

    if venv_type == "group":
        typer.echo(f"Using group venv: {group_path}/.venv\n")
    else:
        typer.echo("⚠️  No venv found, using system Python\n")

    # Use uv pip install with --python to target the venv
    install_cmd = ["uv", "pip", "install", "--python", python_path, "-e", install_spec]

    if verbose:
        typer.echo(f"[verbose] Running command: {' '.join(install_cmd)}")
        typer.echo(f"[verbose] Working directory: {repo_path}\n")

    install_result = subprocess.run(
        install_cmd,
        cwd=str(repo_path),
        check=False,
        capture_output=not verbose,  # Show output in real-time if verbose
        text=True,
    )

    if install_result.returncode != 0:
        typer.echo("⚠️  Warning: Installation failed", err=True)
        if not verbose and install_result.stderr:
            typer.echo(install_result.stderr, err=True)
        raise typer.Exit(1)
    else:
        typer.echo("✅ Package installed successfully\n")
        if verbose and install_result.stdout:
            typer.echo(f"[verbose] Output:\n{install_result.stdout}")

    # Install dependency groups if specified
    if groups:
        groups_list = [g.strip() for g in groups.split(",")]
        typer.echo(f"Installing dependency groups: {', '.join(groups_list)}...\n")

        for group in groups_list:
            group_cmd = [
                "uv",
                "pip",
                "install",
                "--python",
                python_path,
                "--group",
                group,
            ]

            if verbose:
                typer.echo(f"[verbose] Running command: {' '.join(group_cmd)}")
                typer.echo(f"[verbose] Working directory: {repo_path}\n")

            group_result = subprocess.run(
                group_cmd,
                cwd=str(repo_path),
                check=False,
                capture_output=not verbose,  # Show output in real-time if verbose
                text=True,
            )

            if group_result.returncode != 0:
                typer.echo(f"⚠️  Warning: Failed to install group '{group}'", err=True)
                if not verbose and group_result.stderr:
                    typer.echo(group_result.stderr, err=True)
            else:
                typer.echo(f"✅ Group '{group}' installed successfully")
                if verbose and group_result.stdout:
                    typer.echo(f"[verbose] Output:\n{group_result.stdout}")

        typer.echo()  # Empty line at the end
