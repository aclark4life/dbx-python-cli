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
    """Test that init creates a config file."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        config_path = tmp_path / "config.toml"
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert config_path.exists()
        assert "Configuration file created" in result.stdout


def test_repo_init_existing_config_no_overwrite(tmp_path):
    """Test that init doesn't overwrite existing config without confirmation."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        config_path = tmp_path / "config.toml"
        config_path.write_text("existing content")
        mock_get_path.return_value = config_path

        # Simulate user saying "no" to overwrite
        result = runner.invoke(app, ["init"], input="n\n")
        assert result.exit_code == 0
        assert "already exists" in result.stdout
        assert "Aborted" in result.stdout


def test_repo_init_existing_config_with_yes_flag(tmp_path):
    """Test that init --yes overwrites existing config without prompting."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        config_path = tmp_path / "config.toml"
        config_path.write_text("existing content")
        mock_get_path.return_value = config_path

        # Use --yes flag to skip confirmation
        result = runner.invoke(app, ["init", "--yes"])
        assert result.exit_code == 0
        assert "Configuration file created" in result.stdout
        # Should not contain "Aborted" since we skipped the prompt
        assert "Aborted" not in result.stdout


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


def test_repo_clone_list_groups(mock_config):
    """Test that repo clone --list shows available groups."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["repo", "clone", "--list"])
        assert result.exit_code == 0
        assert "Available groups:" in result.stdout
        assert "test" in result.stdout
        assert "2 repositories" in result.stdout


def test_repo_clone_list_groups_short_form(mock_config):
    """Test that repo clone -l works as shortcut for --list."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["repo", "clone", "-l"])
        assert result.exit_code == 0
        assert "Available groups:" in result.stdout
        assert "test" in result.stdout


def test_repo_clone_no_group_shows_error(mock_config):
    """Test that repo clone without -g or -l shows error."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["repo", "clone"])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Group name required" in output


def test_repo_clone_with_fork_user(tmp_path, temp_repos_dir):
    """Test cloning with --fork flag and explicit username."""
    config_path = tmp_path / ".config" / "dbx-python-cli" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    repos_dir_str = str(temp_repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.test]
repos = [
    "git@github.com:mongodb/mongo-python-driver.git",
]
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        with patch("subprocess.run") as mock_run:
            mock_get_path.return_value = config_path
            mock_run.return_value = None

            result = runner.invoke(
                app, ["repo", "clone", "-g", "test", "--fork", "aclark4life"]
            )
            assert result.exit_code == 0
            assert "aclark4life's forks" in result.stdout

            # Verify git clone was called with fork URL
            clone_calls = [
                call for call in mock_run.call_args_list if call[0][0][1] == "clone"
            ]
            assert len(clone_calls) == 1
            assert "aclark4life/mongo-python-driver.git" in clone_calls[0][0][0][2]

            # Verify upstream remote was added
            remote_calls = [
                call for call in mock_run.call_args_list if "remote" in call[0][0]
            ]
            assert len(remote_calls) == 1
            remote_cmd = remote_calls[0][0][0]
            assert "add" in remote_cmd
            assert "upstream" in remote_cmd
            assert "git@github.com:mongodb/mongo-python-driver.git" in remote_cmd


def test_repo_clone_with_fork_from_config(tmp_path, temp_repos_dir):
    """Test cloning with --fork flag using fork_user from config."""
    config_path = tmp_path / ".config" / "dbx-python-cli" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    repos_dir_str = str(temp_repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"
fork_user = "aclark4life"

[repo.groups.test]
repos = [
    "git@github.com:mongodb/mongo-python-driver.git",
]
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        with patch("subprocess.run") as mock_run:
            mock_get_path.return_value = config_path
            mock_run.return_value = None

            # Use --fork without a value to use config default
            result = runner.invoke(app, ["repo", "clone", "-g", "test", "--fork", ""])
            assert result.exit_code == 0
            assert "aclark4life's forks" in result.stdout


def test_repo_clone_fork_without_config_shows_error(tmp_path, temp_repos_dir):
    """Test that --fork without username and no config fork_user shows error."""
    config_path = tmp_path / ".config" / "dbx-python-cli" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    repos_dir_str = str(temp_repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.test]
repos = [
    "git@github.com:mongodb/mongo-python-driver.git",
]
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["repo", "clone", "-g", "test", "--fork", ""])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "fork_user" in output or "GitHub username" in output


def test_repo_clone_fork_https_url(tmp_path, temp_repos_dir):
    """Test cloning with --fork flag using HTTPS URL."""
    config_path = tmp_path / ".config" / "dbx-python-cli" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    repos_dir_str = str(temp_repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.test]
repos = [
    "https://github.com/mongodb/mongo-python-driver.git",
]
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo.get_config_path") as mock_get_path:
        with patch("subprocess.run") as mock_run:
            mock_get_path.return_value = config_path
            mock_run.return_value = None

            result = runner.invoke(
                app, ["repo", "clone", "-g", "test", "--fork", "aclark4life"]
            )
            assert result.exit_code == 0

            # Verify git clone was called with fork URL (HTTPS format)
            clone_calls = [
                call for call in mock_run.call_args_list if call[0][0][1] == "clone"
            ]
            assert len(clone_calls) == 1
            assert "aclark4life/mongo-python-driver.git" in clone_calls[0][0][0][2]
