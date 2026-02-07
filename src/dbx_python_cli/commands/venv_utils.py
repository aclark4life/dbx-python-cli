"""Utilities for virtual environment detection and management."""


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
        group_venv_python = group_path / ".venv" / "bin" / "python"
        if group_venv_python.exists():
            return str(group_venv_python)

    # Fallback to system Python
    return "python"


def get_venv_info(repo_path, group_path=None):
    """
    Get information about which venv will be used.

    Returns:
        tuple: (python_path, venv_type) where venv_type is "group" or "system"
    """
    # Check group-level venv if group_path provided
    if group_path:
        group_venv_python = group_path / ".venv" / "bin" / "python"
        if group_venv_python.exists():
            return str(group_venv_python), "group"

    # Fallback to system Python
    return "python", "system"
