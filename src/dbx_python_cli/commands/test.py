"""Test command for running pytest in repositories."""

import subprocess

import typer

from dbx_python_cli.commands.repo import get_base_dir, get_config

app = typer.Typer(
    help="Test commands",
    context_settings={"help_option_names": ["-h", "--help"]},
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


@app.callback(invoke_without_command=True)
def test_callback(
    ctx: typer.Context,
    repo_name: str = typer.Argument(None, help="Repository name to test"),
    list_repos: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all available repositories",
    ),
    install_extras: bool = typer.Option(
        False,
        "--install",
        "-i",
        help="Install test extras before running tests",
    ),
    keyword: str = typer.Option(
        None,
        "--keyword",
        "-k",
        help="Only run tests matching the given keyword expression (passed to pytest -k)",
    ),
):
    """Run pytest in a cloned repository."""
    # If a subcommand was invoked, don't run this logic
    if ctx.invoked_subcommand is not None:
        return

    try:
        config = get_config()
        base_dir = get_base_dir(config)

        # List repos if requested
        if list_repos:
            repos = find_all_repos(base_dir)
            if not repos:
                typer.echo(f"No repositories found in {base_dir}")
                typer.echo(
                    "Run 'dbx repo clone -g <group>' to clone repositories first."
                )
                raise typer.Exit(0)

            typer.echo(f"Available repositories in {base_dir}:\n")
            for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
                typer.echo(f"  [{repo['group']}] {repo['name']}")
            raise typer.Exit(0)

        # Require repo_name if not listing
        if not repo_name:
            typer.echo(
                "Error: Please specify a repository name or use --list to see available repos.",
                err=True,
            )
            raise typer.Exit(1)

        # Find the repository
        repo = find_repo_by_name(repo_name, base_dir)
        if not repo:
            typer.echo(f"Error: Repository '{repo_name}' not found.", err=True)
            typer.echo("Run 'dbx test --list' to see available repositories.", err=True)
            raise typer.Exit(1)

        repo_path = repo["path"]

        # Install test extras if requested
        if install_extras:
            typer.echo(f"Installing test extras in {repo_path}...\n")
            install_result = subprocess.run(
                ["uv", "pip", "install", "-e", ".[test]"],
                cwd=str(repo_path),
                check=False,
                capture_output=True,
                text=True,
            )

            if install_result.returncode != 0:
                typer.echo(
                    f"⚠️  Warning: Failed to install test extras: {install_result.stderr}",
                    err=True,
                )
                typer.echo("Continuing with test run...\n")
            else:
                typer.echo("✅ Test extras installed successfully\n")

        # Build pytest command
        pytest_cmd = ["pytest"]
        if keyword:
            pytest_cmd.extend(["-k", keyword])
            typer.echo(f"Running pytest -k '{keyword}' in {repo_path}...\n")
        else:
            typer.echo(f"Running pytest in {repo_path}...\n")

        # Run pytest in the repository
        result = subprocess.run(
            pytest_cmd,
            cwd=str(repo_path),
            check=False,
        )

        if result.returncode == 0:
            typer.echo(f"\n✅ Tests passed in {repo_name}")
        else:
            typer.echo(f"\n❌ Tests failed in {repo_name}", err=True)
            raise typer.Exit(result.returncode)

    except typer.Exit:
        # Re-raise typer.Exit to preserve the exit code
        raise
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
