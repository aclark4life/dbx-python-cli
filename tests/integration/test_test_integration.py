"""Integration tests for test commands."""

import shutil
import subprocess
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


# Check if uv is available
def is_uv_available():
    """Check if uv is installed and available."""
    return shutil.which("uv") is not None


# Skip all tests in this module if uv is not available
pytestmark = pytest.mark.skipif(not is_uv_available(), reason="uv is not installed")


def test_test_runs_real_pytest(tmp_path, test_git_repo):
    """Test running real pytest on a repository."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir.mkdir()
    test_group = base_dir / "test"
    test_group.mkdir()

    # Clone the test repo
    cloned_repo = test_group / "test_repo"
    subprocess.run(
        ["git", "clone", str(test_git_repo), str(cloned_repo)],
        check=True,
        capture_output=True,
    )

    # Create a simple test file
    tests_dir = cloned_repo / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_example.py").write_text(
        """def test_example():
    assert True
"""
    )

    base_dir_str = str(base_dir).replace("\\", "/")
    test_repo_str = str(test_git_repo).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"

[repo.groups.test]
repos = [
    "{test_repo_str}",
]
"""
    config_path.write_text(config_content)

    # Create a venv and install pytest
    venv_dir = test_group / ".venv"
    subprocess.run(
        ["python", "-m", "venv", str(venv_dir)], check=True, capture_output=True
    )

    # Install pytest in the venv
    python_exe = venv_dir / "bin" / "python"
    if not python_exe.exists():
        python_exe = venv_dir / "Scripts" / "python.exe"

    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "pytest"],
        check=True,
        capture_output=True,
    )

    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["test", "test_repo"])
        assert result.exit_code == 0
        assert "Running pytest in" in result.stdout
