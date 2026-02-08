"""Utilities for virtual environment detection and management."""

import platform
import subprocess
import sys


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


def get_venv_python(repo_path, group_path=None):
    """
    Get the Python executable from a venv.

    Checks in priority order:
    1. Group-level venv: <group_path>/.venv/bin/python (if group_path provided)
    2. System Python: "python" (fallback)

    Args:
        repo_path: Path to the repository (unused, kept for API compatibility)
        group_path: Path to the group directory (optional)

    Returns:
        str: Path to Python executable or "python" as fallback
    """
    # Check group-level venv if group_path provided
    if group_path:
        # Windows uses Scripts/python.exe, Unix uses bin/python
        if platform.system() == "Windows":
            group_venv_python = group_path / ".venv" / "Scripts" / "python.exe"
        else:
            group_venv_python = group_path / ".venv" / "bin" / "python"

        if group_venv_python.exists():
            return str(group_venv_python)

    # Fallback to system Python
    return "python"


def get_venv_info(repo_path, group_path=None):
    """
    Get information about which venv will be used.

    Returns:
        tuple: (python_path, venv_type) where venv_type is "group", "venv", or "system"
    """
    # Check group-level venv if group_path provided
    if group_path:
        # Windows uses Scripts/python.exe, Unix uses bin/python
        if platform.system() == "Windows":
            group_venv_python = group_path / ".venv" / "Scripts" / "python.exe"
        else:
            group_venv_python = group_path / ".venv" / "bin" / "python"

        if group_venv_python.exists():
            return str(group_venv_python), "group"

    # Check if the default Python is in a venv
    python_path = _get_python_path()
    if _is_venv(python_path):
        return python_path, "venv"

    # Fallback to system Python
    return python_path, "system"
