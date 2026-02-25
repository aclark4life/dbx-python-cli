"""Tests for the fetch command module."""

import re
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


def strip_ansi(text):
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


@pytest.fixture
def temp_repos_dir(tmp_path):
    """Create a temporary repos directory with mock repositories."""
    repos_dir = tmp_path / "repos"
    repos_dir.mkdir(parents=True)

    # Create mock repository structure
    # Group 1: pymongo
    pymongo_dir = repos_dir / "pymongo"
    pymongo_dir.mkdir()

    repo1 = pymongo_dir / "mongo-python-driver"
    repo1.mkdir()
    (repo1 / ".git").mkdir()

    repo2 = pymongo_dir / "specifications"
    repo2.mkdir()
    (repo2 / ".git").mkdir()

    # Group 2: django
    django_dir = repos_dir / "django"
    django_dir.mkdir()

    repo3 = django_dir / "django-mongodb-backend"
    repo3.mkdir()
    (repo3 / ".git").mkdir()

    return repos_dir


@pytest.fixture
def mock_config(tmp_path, temp_repos_dir):
    """Create a mock config file."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"
    # Convert path to use forward slashes for TOML compatibility on Windows
    repos_dir_str = str(temp_repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.pymongo]
repos = [
    "https://github.com/mongodb/mongo-python-driver.git",
    "https://github.com/mongodb/specifications.git",
]

[repo.groups.django]
repos = [
    "https://github.com/aclark4life/django-mongodb-backend.git",
]
"""
    config_path.write_text(config_content)
    return config_path


def test_fetch_help():
    """Test that the fetch help command works."""
    result = runner.invoke(app, ["fetch", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "Fetch updates from remote repositories" in output


def test_fetch_no_repo_name(tmp_path, temp_repos_dir, mock_config):
    """Test that fetch without repo name shows help (no_args_is_help=True)."""
    with patch("dbx_python_cli.commands.fetch.get_config") as mock_get_config:
        mock_get_config.return_value = {
            "repo": {"base_dir": str(temp_repos_dir), "groups": {"pymongo": {}}}
        }
        result = runner.invoke(app, ["fetch"])
        # Exit code 2 means help was shown (no_args_is_help=True)
        assert result.exit_code == 2
        output = strip_ansi(result.stdout)
        assert "Fetch updates from remote repositories" in output


def test_fetch_repo_not_found(tmp_path, temp_repos_dir, mock_config):
    """Test that fetch with non-existent repo shows error."""
    with patch("dbx_python_cli.commands.fetch.get_config") as mock_get_config:
        mock_get_config.return_value = {
            "repo": {"base_dir": str(temp_repos_dir), "groups": {"pymongo": {}}}
        }
        result = runner.invoke(app, ["fetch", "nonexistent-repo"])
        assert result.exit_code == 1
        # Check both stdout and stderr for the error message
        output = strip_ansi(result.stdout + result.stderr)
        assert (
            "Repository 'nonexistent-repo' not found" in output or "not found" in output
        )


def test_fetch_without_args(tmp_path, temp_repos_dir, mock_config):
    """Test fetch command on a single repository without arguments."""
    with patch("dbx_python_cli.commands.fetch.get_config") as mock_get_config:
        mock_get_config.return_value = {
            "repo": {"base_dir": str(temp_repos_dir), "groups": {"pymongo": {}}}
        }
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = runner.invoke(app, ["fetch", "mongo-python-driver"])
            assert result.exit_code == 0
            output = strip_ansi(result.stdout)
            assert "mongo-python-driver: Fetching updates" in output
            # Verify git fetch --all was called
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert call_args == ["git", "fetch", "--all"]


def test_fetch_with_prune_flag(tmp_path, temp_repos_dir, mock_config):
    """Test fetch command with --prune flag."""
    with patch("dbx_python_cli.commands.fetch.get_config") as mock_get_config:
        mock_get_config.return_value = {
            "repo": {"base_dir": str(temp_repos_dir), "groups": {"pymongo": {}}}
        }
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            # Options must come before arguments due to allow_interspersed_args: False
            result = runner.invoke(app, ["fetch", "--prune", "mongo-python-driver"])
            assert result.exit_code == 0
            output = strip_ansi(result.stdout)
            assert "mongo-python-driver: Fetching updates" in output
            # Verify git fetch --all --prune was called
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert call_args == ["git", "fetch", "--all", "--prune"]


def test_fetch_with_group(tmp_path, temp_repos_dir, mock_config):
    """Test fetch command with group option."""
    with patch("dbx_python_cli.commands.fetch.get_config") as mock_get_config:
        mock_get_config.return_value = {
            "repo": {
                "base_dir": str(temp_repos_dir),
                "groups": {
                    "pymongo": {
                        "repos": [
                            "https://github.com/mongodb/mongo-python-driver.git",
                            "https://github.com/mongodb/specifications.git",
                        ]
                    }
                },
            }
        }
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = runner.invoke(app, ["fetch", "-g", "pymongo"])
            assert result.exit_code == 0
            output = strip_ansi(result.stdout)
            assert "Fetching updates for 2 repository(ies)" in output
            assert "mongo-python-driver: Fetching updates" in output
            assert "specifications: Fetching updates" in output
            # Should be called twice (once for each repo)
            assert mock_run.call_count == 2


def test_fetch_with_nonexistent_group(tmp_path, temp_repos_dir, mock_config):
    """Test fetch with non-existent group shows error."""
    with patch("dbx_python_cli.commands.fetch.get_config") as mock_get_config:
        mock_get_config.return_value = {
            "repo": {
                "base_dir": str(temp_repos_dir),
                "groups": {"pymongo": {}},
            }
        }
        result = runner.invoke(app, ["fetch", "-g", "nonexistent"])
        assert result.exit_code == 1
        output = strip_ansi(result.stdout + result.stderr)
        assert "Group 'nonexistent' not found" in output or "not found" in output


def test_verbose_flag_with_fetch_command(tmp_path, temp_repos_dir, mock_config):
    """Test that verbose flag works with fetch command."""
    with patch("dbx_python_cli.commands.fetch.get_config") as mock_get_config:
        mock_get_config.return_value = {
            "repo": {"base_dir": str(temp_repos_dir), "groups": {"pymongo": {}}}
        }
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = runner.invoke(app, ["-v", "fetch", "mongo-python-driver"])
            assert result.exit_code == 0
            output = strip_ansi(result.stdout)
            assert "[verbose]" in output
