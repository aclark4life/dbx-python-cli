"""Configuration management commands."""

import os
import subprocess
from pathlib import Path

import typer

from dbx_python_cli.commands.repo_utils import (
    get_config_path,
    get_default_config_path,
    get_config,
)

app = typer.Typer(
    help="Configuration management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)


@app.command()
def init(
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt and overwrite existing config",
    ),
    remove_base_dir: bool = typer.Option(
        False,
        "--remove-base-dir",
        help="Remove the base_dir directory from the filesystem",
    ),
):
    """Initialize user configuration file."""
    user_config_path = get_config_path()
    default_config_path = get_default_config_path()

    if user_config_path.exists():
        typer.echo(f"Configuration file already exists at {user_config_path}")
        if not yes:
            overwrite = typer.confirm("Do you want to overwrite it?")
            if not overwrite:
                typer.echo("Aborted.")
                raise typer.Exit(0)

    # Create config directory if it doesn't exist
    user_config_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy default config to user config
    if default_config_path.exists():
        import shutil

        shutil.copy(default_config_path, user_config_path)

        # Remove base_dir directory if requested
        if remove_base_dir:
            import tomllib
            import shutil as shutil2

            # Read the config to get base_dir path
            with open(user_config_path, "rb") as f:
                config = tomllib.load(f)

            # Remove base_dir directory from filesystem
            if "repo" in config and "base_dir" in config["repo"]:
                base_dir_path = Path(config["repo"]["base_dir"]).expanduser()

                if base_dir_path.exists():
                    if not yes:
                        confirm = typer.confirm(
                            f"⚠️  This will delete {base_dir_path} and all its contents. Continue?"
                        )
                        if not confirm:
                            typer.echo("Aborted.")
                            raise typer.Exit(0)

                    try:
                        shutil2.rmtree(base_dir_path)
                        typer.echo(
                            f"✅ Configuration file created at {user_config_path}"
                        )
                        typer.echo(f"✅ Removed directory: {base_dir_path}")
                    except Exception as e:
                        typer.echo(
                            f"✅ Configuration file created at {user_config_path}"
                        )
                        typer.echo(
                            f"⚠️  Failed to remove directory {base_dir_path}: {e}",
                            err=True,
                        )
                else:
                    typer.echo(f"✅ Configuration file created at {user_config_path}")
                    typer.echo(f"⚠️  Directory does not exist: {base_dir_path}")
            else:
                typer.echo(f"✅ Configuration file created at {user_config_path}")
                typer.echo("⚠️  No base_dir setting found in config")
        else:
            typer.echo(f"✅ Configuration file created at {user_config_path}")

        typer.echo("\nYou can now edit this file to customize your repository groups.")
    else:
        typer.echo(
            f"Error: Default configuration not found at {default_config_path}",
            err=True,
        )
        raise typer.Exit(1)


@app.command()
def edit():
    """Edit the configuration file with your default editor.

    Opens the configuration file using the editor specified in the EDITOR
    environment variable. If EDITOR is not set, falls back to common editors
    (vim, nano, vi) or uses 'open' on macOS.

    Examples::

        dbx config edit                    # Open with default editor
        EDITOR=code dbx config edit        # Open with VS Code
        EDITOR=nano dbx config edit        # Open with nano
    """
    config_path = get_config_path()

    if not config_path.exists():
        typer.echo(f"❌ Configuration file not found at {config_path}", err=True)
        typer.echo("\nCreate it first using: dbx config init")
        raise typer.Exit(1)

    # Get editor from environment variable
    editor = os.environ.get("EDITOR")

    if not editor:
        # Try common editors in order of preference
        common_editors = ["vim", "nano", "vi"]
        for candidate in common_editors:
            try:
                # Check if editor exists in PATH
                subprocess.run(
                    ["which", candidate],
                    check=True,
                    capture_output=True,
                )
                editor = candidate
                break
            except subprocess.CalledProcessError:
                continue

        # If no common editor found, try 'open' on macOS
        if not editor:
            import platform

            if platform.system() == "Darwin":
                editor = "open"
            else:
                typer.echo(
                    "❌ No editor found. Please set the EDITOR environment variable.",
                    err=True,
                )
                typer.echo("\nExample: export EDITOR=nano")
                raise typer.Exit(1)

    typer.echo(f"📝 Opening {config_path} with {editor}...")

    try:
        # Open the editor
        result = subprocess.run([editor, str(config_path)])

        if result.returncode == 0:
            typer.echo("✅ Configuration file saved")
        else:
            typer.echo(
                f"⚠️  Editor exited with code {result.returncode}",
                err=True,
            )
            raise typer.Exit(result.returncode)
    except FileNotFoundError:
        typer.echo(
            f"❌ Editor '{editor}' not found. Please check your EDITOR environment variable.",
            err=True,
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        typer.echo("\n⚠️  Editing cancelled")
        raise typer.Exit(130)


@app.command()
def show():
    """Display the current configuration.

    Shows the active configuration being used by dbx, including the config file
    location and all settings.

    Examples::

        dbx config show                    # Display current configuration
    """
    config_path = get_config_path()
    default_config_path = get_default_config_path()

    # Determine which config is being used
    if config_path.exists():
        active_config_path = config_path
        config_source = "user config"
    elif default_config_path.exists():
        active_config_path = default_config_path
        config_source = "default config"
    else:
        typer.echo("❌ No configuration file found", err=True)
        typer.echo("\nCreate one using: dbx config init")
        raise typer.Exit(1)

    typer.echo(f"📋 Configuration ({config_source})")
    typer.echo(f"Location: {active_config_path}\n")

    # Load and display the config
    try:
        config = get_config()

        # Display repo settings
        repo_config = config.get("repo", {})
        if repo_config:
            typer.echo("Repository Settings:")
            typer.echo(f"  base_dir: {repo_config.get('base_dir', 'Not set')}")
            fork_user = repo_config.get("fork_user")
            if fork_user:
                typer.echo(f"  fork_user: {fork_user}")
            else:
                typer.echo("  fork_user: Not set")
            typer.echo()

        # Display groups
        groups = repo_config.get("groups", {})
        if groups:
            typer.echo(f"Repository Groups ({len(groups)}):")
            for group_name, group_config in sorted(groups.items()):
                repos = group_config.get("repos", [])
                typer.echo(f"  • {group_name} ({len(repos)} repositories)")
                for repo_url in repos:
                    repo_name = repo_url.split("/")[-1].replace(".git", "")
                    typer.echo(f"    - {repo_name}")

                # Show install_dirs if present
                install_dirs = group_config.get("install_dirs", {})
                if install_dirs:
                    typer.echo("    Install directories:")
                    for repo_name, dirs in install_dirs.items():
                        typer.echo(f"      {repo_name}:")
                        for dir_path in dirs:
                            typer.echo(f"        - {dir_path}")

                # Show test_runner if present
                test_runner = group_config.get("test_runner", {})
                if test_runner:
                    typer.echo("    Custom test runners:")
                    for repo_name, runner_path in test_runner.items():
                        typer.echo(f"      {repo_name}: {runner_path}")

                # Show test_env if present
                test_env = group_config.get("test_env", {})
                if test_env:
                    typer.echo("    Test environment variables:")
                    for repo_name, env_vars in test_env.items():
                        if isinstance(env_vars, dict):
                            typer.echo(f"      {repo_name}:")
                            for var_name, var_value in env_vars.items():
                                typer.echo(f"        {var_name}={var_value}")
            typer.echo()
        else:
            typer.echo("No repository groups configured\n")

        typer.echo("To edit: dbx config edit")
        typer.echo("To initialize user config: dbx config init")

    except Exception as e:
        typer.echo(f"❌ Error reading configuration: {e}", err=True)
        raise typer.Exit(1)
