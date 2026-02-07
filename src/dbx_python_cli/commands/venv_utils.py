"""Utilities for virtual environment detection and management."""


def get_venv_python(repo_path, group_path=None):
    """
    Get the Python executable from a venv.

    Checks in priority order:
    1. Repo-level venv: <repo_path>/.venv/bin/python
    2. Group-level venv: <group_path>/.venv/bin/python (if group_path provided)
    3. System Python: "python" (fallback)

    Args:
        repo_path: Path to the repository
        group_path: Path to the group directory (optional)

    Returns:
        str: Path to Python executable or "python" as fallback
    """
    # Check repo-level venv first
    repo_venv_python = repo_path / ".venv" / "bin" / "python"
    if repo_venv_python.exists():
        return str(repo_venv_python)

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
        tuple: (python_path, venv_type) where venv_type is "repo", "group", or "system"
    """
    # Check repo-level venv first
    repo_venv_python = repo_path / ".venv" / "bin" / "python"
    if repo_venv_python.exists():
        return str(repo_venv_python), "repo"

    # Check group-level venv if group_path provided
    if group_path:
        group_venv_python = group_path / ".venv" / "bin" / "python"
        if group_venv_python.exists():
            return str(group_venv_python), "group"

    # Fallback to system Python
    return "python", "system"
