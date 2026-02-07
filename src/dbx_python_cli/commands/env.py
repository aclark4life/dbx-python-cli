"""Virtual environment management commands."""

import subprocess

import typer

from dbx_python_cli.commands.repo import get_base_dir, get_config, get_repo_groups

app = typer.Typer(
    help="Virtual environment management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def init(
    ctx: typer.Context,
    group: str = typer.Option(
        ...,
        "--group",
        "-g",
        help="Repository group to create venv for (e.g., pymongo, langchain, django)",
    ),
    python: str = typer.Option(
        None,
        "--python",
        "-p",
        help="Python version to use (e.g., 3.11, 3.12)",
    ),
):
    """Create a virtual environment for a repository group."""
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        groups = get_repo_groups(config)

        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}")
            typer.echo(f"[verbose] Available groups: {list(groups.keys())}\n")

        if group not in groups:
            typer.echo(f"Error: Group '{group}' not found in configuration.", err=True)
            typer.echo(f"Available groups: {', '.join(groups.keys())}", err=True)
            raise typer.Exit(1)

        # Group directory
        group_dir = base_dir / group
        if not group_dir.exists():
            typer.echo(
                f"Error: Group directory '{group_dir}' does not exist.", err=True
            )
            typer.echo(
                f"Clone the group first with: dbx repo clone -g {group}", err=True
            )
            raise typer.Exit(1)

        # Venv path
        venv_path = group_dir / ".venv"
        if venv_path.exists():
            typer.echo(f"Virtual environment already exists at {venv_path}")
            overwrite = typer.confirm("Do you want to recreate it?")
            if not overwrite:
                typer.echo("Aborted.")
                raise typer.Exit(0)
            # Remove existing venv
            import shutil

            shutil.rmtree(venv_path)

        # Create venv using uv
        typer.echo(
            f"Creating virtual environment for group '{group}' at {venv_path}...\n"
        )

        venv_cmd = ["uv", "venv", str(venv_path)]
        if python:
            venv_cmd.extend(["--python", python])

        if verbose:
            typer.echo(f"[verbose] Running command: {' '.join(venv_cmd)}")
            typer.echo(f"[verbose] Working directory: {group_dir}\n")

        result = subprocess.run(
            venv_cmd,
            cwd=str(group_dir),
            check=False,
            capture_output=not verbose,
            text=True,
        )

        if result.returncode != 0:
            typer.echo("❌ Failed to create virtual environment", err=True)
            if not verbose and result.stderr:
                typer.echo(result.stderr, err=True)
            raise typer.Exit(1)

        typer.echo(f"✅ Virtual environment created at {venv_path}")
        typer.echo(f"\nTo activate: source {venv_path}/bin/activate")
        typer.echo("Or use: dbx install <repo> to install dependencies using this venv")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list(ctx: typer.Context):
    """List virtual environments for all groups."""
    # Get verbose flag from parent context
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        config = get_config()
        base_dir = get_base_dir(config)
        groups = get_repo_groups(config)

        if verbose:
            typer.echo(f"[verbose] Using base directory: {base_dir}\n")

        typer.echo("Virtual environments:\n")

        found_any = False
        for group_name in groups.keys():
            group_dir = base_dir / group_name
            venv_path = group_dir / ".venv"

            if venv_path.exists():
                found_any = True
                python_path = venv_path / "bin" / "python"
                if python_path.exists():
                    # Get Python version
                    result = subprocess.run(
                        [str(python_path), "--version"],
                        capture_output=True,
                        text=True,
                    )
                    version = (
                        result.stdout.strip() if result.returncode == 0 else "unknown"
                    )
                    typer.echo(f"  ✅ {group_name}: {venv_path} ({version})")
                else:
                    typer.echo(f"  ⚠️  {group_name}: {venv_path} (invalid)")
            else:
                typer.echo(
                    f"  ❌ {group_name}: No venv (create with: dbx env init -g {group_name})"
                )

        if not found_any:
            typer.echo("  No virtual environments found.")
            typer.echo("\nCreate one with: dbx env init -g <group>")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
