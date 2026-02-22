"""Utilities for virtual environment detection and management."""

import platform
import subprocess
import sys

import typer


def _get_python_path():
    """
    Get the actual path to the Python executable.

    Returns:
        str: Full path to the Python executable
    """
    try:
        # Windows uses 'where', Unix uses 'which'
        cmd = "where" if platform.system() == "Windows" else "which"
        result = subprocess.run(
            [cmd, "python"],
            capture_output=True,
            text=True,
            check=True,
        )
        # 'where' on Windows can return multiple paths, take the first one
        output = result.stdout.strip()
        return output.split("\n")[0] if output else sys.executable
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to sys.executable if command fails
        return sys.executable


def _is_venv(python_path):
    """
    Check if a Python executable is in a virtual environment.

    Args:
        python_path: Path to Python executable

    Returns:
        bool: True if in a venv, False otherwise
    """
    try:
        result = subprocess.run(
            [
                python_path,
                "-c",
                "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().lower() == "true"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_venv_python(repo_path, group_path=None, base_path=None):
    """
    Get the Python executable from a venv.

    Checks in priority order:
    1. Base directory venv: <base_path>/.venv/bin/python (if base_path provided)
    2. Repository-level venv: <repo_path>/.venv/bin/python
    3. Group-level venv: <group_path>/.venv/bin/python (if group_path provided)
    4. System Python: "python" (fallback)

    Args:
        repo_path: Path to the repository
        group_path: Path to the group directory (optional)
        base_path: Path to the base directory (optional)

    Returns:
        str: Path to Python executable or "python" as fallback
    """
    # Windows uses Scripts/python.exe, Unix uses bin/python
    if platform.system() == "Windows":
        python_subpath = "Scripts/python.exe"
    else:
        python_subpath = "bin/python"

    # Check base directory venv if base_path provided
    if base_path:
        base_venv_python = base_path / ".venv" / python_subpath
        if base_venv_python.exists():
            return str(base_venv_python)

    # Check repository-level venv
    if repo_path:
        repo_venv_python = repo_path / ".venv" / python_subpath
        if repo_venv_python.exists():
            return str(repo_venv_python)

    # Check group-level venv if group_path provided
    if group_path:
        group_venv_python = group_path / ".venv" / python_subpath
        if group_venv_python.exists():
            return str(group_venv_python)

    # Fallback to system Python
    return "python"


def get_venv_info(repo_path, group_path=None, base_path=None):
    """
    Get information about which venv will be used.

    Checks in priority order:
    1. Base directory venv
    2. Repository-level venv
    3. Group-level venv
    4. Activated venv

    Returns:
        tuple: (python_path, venv_type) where venv_type is "base", "repo", "group", or "venv"

    Raises:
        typer.Exit: If no virtual environment is found (system Python detected)
    """
    # Windows uses Scripts/python.exe, Unix uses bin/python
    if platform.system() == "Windows":
        python_subpath = "Scripts/python.exe"
    else:
        python_subpath = "bin/python"

    # Check base directory venv if base_path provided
    if base_path:
        base_venv_python = base_path / ".venv" / python_subpath
        if base_venv_python.exists():
            return str(base_venv_python), "base"

    # Check repository-level venv
    if repo_path:
        repo_venv_python = repo_path / ".venv" / python_subpath
        if repo_venv_python.exists():
            return str(repo_venv_python), "repo"

    # Check group-level venv if group_path provided
    if group_path:
        group_venv_python = group_path / ".venv" / python_subpath
        if group_venv_python.exists():
            return str(group_venv_python), "group"

    # Check if the default Python is in a venv
    python_path = _get_python_path()
    if _is_venv(python_path):
        return python_path, "venv"

    # System Python detected - error out
    typer.echo(
        "❌ Error: No virtual environment found. Installation to system Python is not allowed.",
        err=True,
    )
    typer.echo("\nTo fix this, create a virtual environment:", err=True)
    typer.echo("  dbx env init              (base dir - recommended)", err=True)

    if group_path:
        group_name = group_path.name
        typer.echo(f"  dbx env init -g {group_name}  (group level)", err=True)

    if repo_path:
        repo_name = repo_path.name
        typer.echo(f"  dbx env init {repo_name}      (repo level)", err=True)

    typer.echo("\nOr activate an existing virtual environment before running dbx install.", err=True)
    raise typer.Exit(1)
