"""Install command for installing dependencies in repositories."""

import subprocess
import tomllib
from pathlib import Path
from typing import Optional

import typer

from dbx_python_cli.commands.repo_utils import (
    find_all_repos,
    find_repo_by_name,
    get_base_dir,
    get_config,
    get_install_dirs,
)
from dbx_python_cli.commands.venv_utils import get_venv_info


def install_frontend_if_exists(repo_path, verbose=False):
    """
    Check if a frontend directory exists and install npm dependencies if found.

    Args:
        repo_path: Path to the repository/project root
        verbose: Whether to show verbose output

    Returns:
        bool: True if frontend was found and installed successfully, False if no frontend or failed
    """
    frontend_path = repo_path / "frontend"
    package_json = frontend_path / "package.json"

    if not frontend_path.exists() or not package_json.exists():
        return False

    typer.echo(f"\n🎨 Frontend detected at {frontend_path}")
    typer.echo("📦 Installing npm dependencies...")

    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd=frontend_path,
            check=False,
            capture_output=not verbose,
            text=True,
        )

        if result.returncode != 0:
            typer.echo("⚠️  npm install failed", err=True)
            if not verbose and result.stderr:
                typer.echo(result.stderr, err=True)
            return False

        typer.echo("✅ Frontend dependencies installed successfully")
        return True

    except FileNotFoundError:
        typer.echo(
            "⚠️  npm not found. Please ensure Node.js and npm are installed.",
            err=True,
        )
        return False
    except Exception as e:
        typer.echo(f"⚠️  Unexpected error during frontend installation: {e}", err=True)
        return False


app = typer.Typer(
    help="Install commands",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": False,
    },
    no_args_is_help=True,
)


def get_package_options(work_dir):
    """
    Extract available extras and dependency groups from pyproject.toml.

    Args:
        work_dir: Path to the directory containing pyproject.toml

    Returns:
        dict: Dictionary with 'extras' and 'dependency_groups' lists
    """
    pyproject_path = work_dir / "pyproject.toml"

    if not pyproject_path.exists():
        return {"extras": [], "dependency_groups": []}

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        # Extract extras from [project.optional-dependencies]
        extras = []
        if "project" in data and "optional-dependencies" in data["project"]:
            extras = list(data["project"]["optional-dependencies"].keys())

        # Also check for hatch metadata hooks (used when optional-dependencies is dynamic)
        if (
            not extras
            and "tool" in data
            and "hatch" in data["tool"]
            and "metadata" in data["tool"]["hatch"]
            and "hooks" in data["tool"]["hatch"]["metadata"]
            and "requirements_txt" in data["tool"]["hatch"]["metadata"]["hooks"]
        ):
            hatch_hooks = data["tool"]["hatch"]["metadata"]["hooks"]["requirements_txt"]
            if "optional-dependencies" in hatch_hooks:
                extras = list(hatch_hooks["optional-dependencies"].keys())

        # Extract dependency groups from [dependency-groups] (PEP 735)
        dependency_groups = []
        if "dependency-groups" in data:
            dependency_groups = list(data["dependency-groups"].keys())

        return {
            "extras": sorted(extras),
            "dependency_groups": sorted(dependency_groups),
        }

    except Exception:
        # If we can't parse the file, return empty lists
        return {"extras": [], "dependency_groups": []}


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
        str: "success" if successful, "skipped" if no setup.py/pyproject.toml, "failed" otherwise
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

    # Check if the directory has an installable package
    has_setup_py = (work_dir / "setup.py").exists()
    has_pyproject_toml = (work_dir / "pyproject.toml").exists()

    if not has_setup_py and not has_pyproject_toml:
        typer.echo(
            f"⚠️  Skipping {display_path}: No setup.py or pyproject.toml found", err=True
        )
        return "skipped"

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
        return "failed"

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
                return "failed"

            if verbose and group_result.stdout:
                typer.echo(f"[verbose] Output:\n{group_result.stdout}")

    return "success"


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
    dependency_groups: Optional[str] = typer.Option(
        None,
        "--dependency-groups",
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
        help="Show repository status (cloned vs available)",
    ),
    show_options: bool = typer.Option(
        False,
        "--show-options",
        help="Show available extras and dependency groups for the repository",
    ),
    repo_group: Optional[str] = typer.Option(
        None,
        "-G",
        help="Specify which group to use when repo exists in multiple groups (for single repo operations)",
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
        from dbx_python_cli.commands.repo_utils import list_repos as list_repos_func

        output = list_repos_func(base_dir, config=config)
        if output:
            typer.echo(f"Base directory: {base_dir}\n")
            typer.echo(output)
            typer.echo(
                "\nLegend: ✓ = cloned, ○ = available to clone, ? = cloned but not in config"
            )
        else:
            typer.echo(f"Base directory: {base_dir}\n")
            typer.echo("No repositories found.")
            typer.echo("\nClone repositories using: dbx clone -g <group>")
        return

    # Handle --show-options flag
    if show_options:
        # Case 1: Show options for all repos in a group (-g <group>)
        if group and not repo_name:
            group_path = base_dir / group
            if not group_path.exists():
                typer.echo(
                    f"❌ Error: Group '{group}' not found in {base_dir}", err=True
                )
                raise typer.Exit(1)

            # Find all repos in this group
            all_repos = find_all_repos(base_dir)
            group_repos = [r for r in all_repos if r["group"] == group]

            if not group_repos:
                typer.echo(
                    f"❌ Error: No repositories found in group '{group}'", err=True
                )
                typer.echo(f"\nClone repositories using: dbx clone -g {group}")
                raise typer.Exit(1)

            typer.echo(f"📦 Showing options for all repositories in group '{group}':\n")

            for repo in group_repos:
                repo_path = repo["path"]
                repo_name = repo["name"]
                install_dirs = get_install_dirs(config, group, repo_name)

                if install_dirs:
                    # Monorepo
                    typer.echo(
                        f"  {repo_name} (monorepo with {len(install_dirs)} packages):"
                    )
                    for install_dir in install_dirs:
                        work_dir = repo_path / install_dir
                        options = get_package_options(work_dir)
                        typer.echo(f"    Package: {install_dir}")
                        if options["extras"]:
                            typer.echo(f"      Extras: {', '.join(options['extras'])}")
                        else:
                            typer.echo("      Extras: (none)")
                        if options["dependency_groups"]:
                            typer.echo(
                                f"      Dependency groups: {', '.join(options['dependency_groups'])}"
                            )
                        else:
                            typer.echo("      Dependency groups: (none)")
                else:
                    # Regular repo
                    options = get_package_options(repo_path)
                    typer.echo(f"  {repo_name}:")
                    if options["extras"]:
                        typer.echo(f"    Extras: {', '.join(options['extras'])}")
                    else:
                        typer.echo("    Extras: (none)")
                    if options["dependency_groups"]:
                        typer.echo(
                            f"    Dependency groups: {', '.join(options['dependency_groups'])}"
                        )
                    else:
                        typer.echo("    Dependency groups: (none)")
                typer.echo()

            return

        # Case 2: Show options for a single repo
        if not repo_name:
            typer.echo(
                "❌ Error: Repository name required with --show-options", err=True
            )
            typer.echo("\nUsage: dbx install <repo-name> --show-options")
            typer.echo("   or: dbx install --show-options -g <group>")
            raise typer.Exit(1)

        # Find the repository, optionally filtering by -G flag
        if repo_group:
            # Look for repo in the specified group (-G flag)
            group_path = base_dir / repo_group
            if not group_path.exists():
                typer.echo(
                    f"❌ Error: Group '{repo_group}' not found in {base_dir}", err=True
                )
                raise typer.Exit(1)

            repo_path = group_path / repo_name
            if not repo_path.exists() or not (repo_path / ".git").exists():
                typer.echo(
                    f"❌ Error: Repository '{repo_name}' not found in group '{repo_group}'",
                    err=True,
                )
                typer.echo("\nUse 'dbx install --list' to see available repositories")
                raise typer.Exit(1)

            selected_group = repo_group
        else:
            # Find the repository across all groups
            repo = find_repo_by_name(repo_name, base_dir)
            if not repo:
                typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
                typer.echo("\nUse 'dbx install --list' to see available repositories")
                raise typer.Exit(1)

            repo_path = repo["path"]
            selected_group = repo["group"]

        install_dirs = get_install_dirs(config, selected_group, repo_name)

        if install_dirs:
            # Monorepo: show options for each package
            typer.echo(f"📦 {repo_name} (monorepo with {len(install_dirs)} packages)\n")

            for install_dir in install_dirs:
                work_dir = repo_path / install_dir
                options = get_package_options(work_dir)

                typer.echo(f"  Package: {install_dir}")
                if options["extras"]:
                    typer.echo(f"    Extras: {', '.join(options['extras'])}")
                else:
                    typer.echo("    Extras: (none)")

                if options["dependency_groups"]:
                    typer.echo(
                        f"    Dependency groups: {', '.join(options['dependency_groups'])}"
                    )
                else:
                    typer.echo("    Dependency groups: (none)")
                typer.echo()
        else:
            # Regular repo: show options for the package
            options = get_package_options(repo_path)

            typer.echo(f"📦 {repo_name}\n")
            if options["extras"]:
                typer.echo(f"  Extras: {', '.join(options['extras'])}")
            else:
                typer.echo("  Extras: (none)")

            if options["dependency_groups"]:
                typer.echo(
                    f"  Dependency groups: {', '.join(options['dependency_groups'])}"
                )
            else:
                typer.echo("  Dependency groups: (none)")

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
            typer.echo(f"\nClone repositories using: dbx clone -g {group}")
            raise typer.Exit(1)

        typer.echo(f"Installing all repositories in group '{group}'...\n")

        # Install each repo in the group
        failed_items = []
        skipped_items = []
        total_items = 0

        for repo in group_repos:
            repo_path = Path(repo["path"])
            typer.echo(f"{'=' * 60}")
            typer.echo(f"Installing: {repo['name']}")
            typer.echo(f"{'=' * 60}\n")

            # Detect venv
            python_path, venv_type = get_venv_info(repo_path, group_path)

            if verbose:
                typer.echo(f"[verbose] Venv type: {venv_type}")
                typer.echo(f"[verbose] Python: {python_path}\n")

            # Show venv info
            if venv_type == "group":
                typer.echo(f"Using group venv: {group_path}/.venv\n")
            elif venv_type == "venv":
                typer.echo(f"Using venv: {python_path}\n")
            else:
                typer.echo(f"⚠️  No venv found, using system Python: {python_path}\n")

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

                    result = install_package(
                        repo_path,
                        python_path,
                        install_dir=install_dir,
                        extras=extras,
                        groups=dependency_groups,
                        verbose=verbose,
                    )

                    if result == "success":
                        typer.echo(f"  ✅ {install_dir} installed successfully\n")
                    elif result == "skipped":
                        skipped_items.append(f"{repo['name']}/{install_dir}")
                    else:
                        failed_items.append(f"{repo['name']}/{install_dir}")
            else:
                # Regular repo: install from root
                total_items += 1

                result = install_package(
                    repo_path,
                    python_path,
                    install_dir=None,
                    extras=extras,
                    groups=dependency_groups,
                    verbose=verbose,
                )

                if result == "success":
                    typer.echo(f"✅ {repo['name']} installed successfully")
                    # Check for frontend and install if present
                    install_frontend_if_exists(repo_path, verbose=verbose)
                    typer.echo()
                elif result == "skipped":
                    skipped_items.append(repo["name"])
                else:
                    failed_items.append(repo["name"])

        # Summary
        typer.echo(f"\n{'=' * 60}")
        typer.echo("Installation Summary")
        typer.echo(f"{'=' * 60}")
        typer.echo(f"Total packages: {total_items}")
        typer.echo(f"Successful: {total_items - len(failed_items) - len(skipped_items)}")
        if skipped_items:
            typer.echo(f"Skipped: {len(skipped_items)}")
        if failed_items:
            typer.echo(f"Failed: {len(failed_items)}")

        if skipped_items:
            typer.echo("\nSkipped repositories:")
            for item_name in skipped_items:
                typer.echo(f"  • {item_name}")

        if failed_items:
            typer.echo("\nFailed repositories:")
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

    # Determine which group to use
    if group:
        # Use specified group
        group_path = base_dir / group
        if not group_path.exists():
            typer.echo(f"❌ Error: Group '{group}' not found in {base_dir}", err=True)
            raise typer.Exit(1)

        # Look for the repo in the specified group
        repo_path = group_path / repo_name
        if not repo_path.exists() or not (repo_path / ".git").exists():
            typer.echo(
                f"❌ Error: Repository '{repo_name}' not found in group '{group}'",
                err=True,
            )
            typer.echo("\nRun 'dbx install --list' to see available repositories")
            raise typer.Exit(1)

        # Build repo dict for consistency with find_repo_by_name
        repo = {
            "name": repo_name,
            "path": repo_path,
            "group": group,
        }
    else:
        # Find the repository (will return first match if multiple exist)
        repo = find_repo_by_name(repo_name, base_dir)
        if not repo:
            typer.echo(f"❌ Error: Repository '{repo_name}' not found", err=True)
            typer.echo("\nRun 'dbx install --list' to see available repositories")
            raise typer.Exit(1)

        # Check if repo exists in multiple groups
        all_repos = find_all_repos(base_dir)
        matching_repos = [r for r in all_repos if r["name"] == repo_name]
        if len(matching_repos) > 1:
            groups = [r["group"] for r in matching_repos]
            typer.echo(
                f"⚠️  Warning: Repository '{repo_name}' found in multiple groups: {', '.join(groups)}",
                err=True,
            )
            typer.echo(
                f"⚠️  Using '{repo['group']}' group. Use -g to specify a different group.\n",
                err=True,
            )

        repo_path = Path(repo["path"])
        # Default to repo's own group
        group_path = repo_path.parent

    # Detect venv
    python_path, venv_type = get_venv_info(repo_path, group_path)

    if verbose:
        typer.echo(f"[verbose] Venv type: {venv_type}")
        typer.echo(f"[verbose] Python: {python_path}\n")

    # Show venv info
    if venv_type == "group":
        typer.echo(f"Using group venv: {group_path}/.venv\n")
    elif venv_type == "venv":
        typer.echo(f"Using venv: {python_path}\n")
    else:
        typer.echo(f"⚠️  No venv found, using system Python: {python_path}\n")

    # Check if this repo has install_dirs (monorepo)
    install_dirs = get_install_dirs(config, repo["group"], repo["name"])

    if install_dirs:
        # Monorepo: install each directory separately
        typer.echo(f"Monorepo detected: installing {len(install_dirs)} packages...\n")

        failed_items = []
        skipped_items = []
        for install_dir in install_dirs:
            typer.echo(f"  → Installing from {install_dir}...")

            result = install_package(
                repo_path,
                python_path,
                install_dir=install_dir,
                extras=extras,
                groups=dependency_groups,
                verbose=verbose,
            )

            if result == "success":
                typer.echo(f"  ✅ {install_dir} installed successfully\n")
            elif result == "skipped":
                skipped_items.append(f"{repo['name']}/{install_dir}")
            else:
                failed_items.append(f"{repo['name']}/{install_dir}")

        if skipped_items:
            typer.echo(f"\n⚠️  Skipped {len(skipped_items)} package(s):")
            for item in skipped_items:
                typer.echo(f"  • {item}")

        if failed_items:
            typer.echo(f"\n❌ Failed to install {len(failed_items)} package(s):")
            for item in failed_items:
                typer.echo(f"  • {item}")
            raise typer.Exit(1)
        else:
            typer.echo(f"\n✅ All packages in {repo['name']} installed successfully!")

        # Check for frontend and install if present (even for monorepos)
        install_frontend_if_exists(repo_path, verbose=verbose)
    else:
        # Regular repo: install from root
        typer.echo(f"Installing dependencies in {repo_path}...")

        result = install_package(
            repo_path,
            python_path,
            install_dir=None,
            extras=extras,
            groups=dependency_groups,
            verbose=verbose,
        )

        if result == "failed":
            raise typer.Exit(1)
        elif result == "skipped":
            # Already printed skip message, just exit cleanly
            return

        typer.echo("✅ Package installed successfully")

        # Check for frontend and install if present
        install_frontend_if_exists(repo_path, verbose=verbose)
