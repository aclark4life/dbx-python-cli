"""Tests for the repo command module."""

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

[repo.groups.test]
repos = [
    "https://github.com/test/repo1.git",
    "https://github.com/test/repo2.git",
]
"""
    config_path.write_text(config_content)
    return config_path


def test_repo_help():
    """Test that the repo help command works."""
    result = runner.invoke(app, ["repo", "--help"])
    assert result.exit_code == 0
    assert "Repository management commands" in result.stdout


def test_repo_init_creates_config(tmp_path):
    """Test that repo init creates a config file."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        config_path = tmp_path / "config.toml"
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["repo", "init"])
        assert result.exit_code == 0
        assert config_path.exists()
        assert "Configuration file created" in result.stdout


def test_repo_init_existing_config_no_overwrite(tmp_path):
    """Test that repo init doesn't overwrite existing config without confirmation."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        config_path = tmp_path / "config.toml"
        config_path.write_text("existing content")
        mock_get_path.return_value = config_path

        # Simulate user saying "no" to overwrite
        result = runner.invoke(app, ["repo", "init"], input="n\n")
        assert result.exit_code == 0
        assert "already exists" in result.stdout
        assert "Aborted" in result.stdout


def test_repo_clone_help():
    """Test that the repo clone help command works."""
    result = runner.invoke(app, ["repo", "clone", "--help"])
    assert result.exit_code == 0
    assert "Clone repositories from a specified group" in result.stdout


def test_repo_clone_invalid_group(tmp_path, mock_config):
    """Test that repo clone fails with invalid group."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["repo", "clone", "-g", "nonexistent"])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Group 'nonexistent' not found" in output


def test_repo_clone_success(tmp_path, mock_config, temp_repos_dir):
    """Test successful repo clone."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        with patch("subprocess.run") as mock_run:
            mock_get_path.return_value = mock_config
            mock_run.return_value = None

            result = runner.invoke(app, ["repo", "clone", "-g", "test"])
            assert result.exit_code == 0
            assert "Cloning 2 repository(ies)" in result.stdout
            assert "test" in result.stdout


def test_repo_clone_creates_group_directory(tmp_path, mock_config, temp_repos_dir):
    """Test that repo clone creates group subdirectory."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        with patch("subprocess.run") as mock_run:
            mock_get_path.return_value = mock_config
            mock_run.return_value = None

            result = runner.invoke(app, ["repo", "clone", "-g", "test"])
            assert result.exit_code == 0

            # Check that group directory was created
            group_dir = temp_repos_dir / "test"
            assert group_dir.exists()
            assert group_dir.is_dir()


def test_repo_clone_skips_existing(tmp_path, mock_config, temp_repos_dir):
    """Test that repo clone skips existing repositories."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        # Create existing repo
        group_dir = temp_repos_dir / "test"
        group_dir.mkdir(parents=True)
        existing_repo = group_dir / "repo1"
        existing_repo.mkdir()

        with patch("subprocess.run"):
            result = runner.invoke(app, ["repo", "clone", "-g", "test"])
            assert result.exit_code == 0
            assert "already exists" in result.stdout


def test_repo_clone_git_failure(mock_config, temp_repos_dir):
    """Test that repo clone handles git clone failures gracefully."""
    import subprocess

    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        # Mock subprocess.run to raise CalledProcessError
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git clone", stderr="fatal: repository not found"
            )
            result = runner.invoke(app, ["repo", "clone", "-g", "test"])
            # Should still exit 0 (doesn't fail the whole command)
            assert result.exit_code == 0
            # Check stderr for error message
            output = result.stdout + result.stderr
            assert "Failed to clone" in output


def test_repo_clone_empty_repos_list(temp_config_dir, temp_repos_dir):
    """Test that repo clone handles groups with no repos defined."""
    config_path = temp_config_dir / "config.toml"
    repos_dir_str = str(temp_repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.empty]
repos = []
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path
        result = runner.invoke(app, ["repo", "clone", "-g", "empty"])
        assert result.exit_code == 1
        # Check both stdout and stderr
        output = result.stdout + result.stderr
        assert "No repositories defined for group 'empty'" in output


def test_get_config_fallback_to_default(temp_config_dir):
    """Test that get_config falls back to default config when user config doesn't exist."""
    from dbx_python_cli.commands.repo import get_config

    # Don't create user config, should fall back to package default
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        # Point to non-existent user config
        mock_get_path.return_value = temp_config_dir / "nonexistent.toml"
        config = get_config()
        # Should have loaded the default config which has repo.groups structure
        assert "repo" in config
        assert "groups" in config["repo"]
        assert "pymongo" in config["repo"]["groups"]
