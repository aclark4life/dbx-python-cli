"""Tests for the env command module."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def temp_repos_dir(tmp_path):
    """Create a temporary repos directory."""
    repos_dir = tmp_path / "repos"
    repos_dir.mkdir(parents=True)
    return repos_dir


@pytest.fixture
def mock_config(temp_config_dir, temp_repos_dir):
    """Create a mock config file."""
    config_path = temp_config_dir / "config.toml"
    # Convert path to use forward slashes for TOML compatibility on Windows
    repos_dir_str = str(temp_repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.pymongo]
repos = [
    "git@github.com:mongodb/mongo-python-driver.git",
]

[repo.groups.langchain]
repos = [
    "git@github.com:langchain-ai/langchain-mongodb.git",
]
"""
    config_path.write_text(config_content)
    return config_path


def test_env_help():
    """Test that the env help command works."""
    result = runner.invoke(app, ["env", "--help"])
    assert result.exit_code == 0
    assert "Virtual environment management commands" in result.stdout


def test_env_init_list_groups(mock_config, temp_repos_dir):
    """Test that env init --list shows available groups."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        # Create one group directory with venv
        pymongo_dir = temp_repos_dir / "pymongo"
        pymongo_dir.mkdir(parents=True)
        venv_dir = pymongo_dir / ".venv"
        venv_dir.mkdir()

        result = runner.invoke(app, ["env", "init", "--list"])
        assert result.exit_code == 0
        assert "Available groups:" in result.stdout
        assert "pymongo" in result.stdout
        assert "venv exists" in result.stdout
        assert "langchain" in result.stdout
        assert "no venv" in result.stdout


def test_env_init_list_groups_short_form(mock_config):
    """Test that env init -l works as shortcut for --list."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["env", "init", "-l"])
        assert result.exit_code == 0
        assert "Available groups:" in result.stdout
        assert "pymongo" in result.stdout
        assert "langchain" in result.stdout


def test_env_init_no_group_shows_error(mock_config):
    """Test that env init without -g or -l shows error."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["env", "init"])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Group name required" in output
