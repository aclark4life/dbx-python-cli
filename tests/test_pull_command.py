"""Tests for the pull command module."""

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
def mock_config(temp_repos_dir):
    """Mock configuration for testing."""
    return {
        "repo": {
            "base_dir": str(temp_repos_dir),
            "groups": {
                "pymongo": {
                    "repos": [
                        "git@github.com:mongodb/mongo-python-driver.git",
                        "git@github.com:mongodb/specifications.git",
                    ]
                },
                "django": {
                    "repos": [
                        "git@github.com:mongodb-labs/django-mongodb-backend.git",
                    ]
                },
            },
        }
    }


def test_pull_single_repo_success(temp_repos_dir, mock_config):
    """Test pulling a single repository successfully."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        with patch("subprocess.run") as mock_run:
            # Mock successful git pull
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Already up to date.\n",
                stderr="",
            )

            result = runner.invoke(app, ["pull", "mongo-python-driver"])

            assert result.exit_code == 0
            output = strip_ansi(result.stdout)
            assert "mongo-python-driver: Pulling updates" in output
            assert "mongo-python-driver: Already up to date" in output


def test_pull_single_repo_with_updates(temp_repos_dir, mock_config):
    """Test pulling a single repository with updates."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        with patch("subprocess.run") as mock_run:
            # Mock git pull with updates
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Updating abc123..def456\nFast-forward\n file.py | 2 +-\n",
                stderr="",
            )

            result = runner.invoke(app, ["pull", "mongo-python-driver"])

            assert result.exit_code == 0
            output = strip_ansi(result.stdout)
            assert "mongo-python-driver: Pulling updates" in output
            assert "mongo-python-driver: Pulled successfully" in output


def test_pull_single_repo_with_rebase(temp_repos_dir, mock_config):
    """Test pulling a single repository with rebase option."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        with patch("subprocess.run") as mock_run:
            # Mock successful git pull --rebase
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Already up to date.\n",
                stderr="",
            )

            result = runner.invoke(app, ["pull", "--rebase", "mongo-python-driver"])

            assert result.exit_code == 0
            # Verify --rebase was passed to git
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "git" in call_args[0][0]
            assert "pull" in call_args[0][0]
            assert "--rebase" in call_args[0][0]


def test_pull_group_success(temp_repos_dir, mock_config):
    """Test pulling all repositories in a group."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        with patch("subprocess.run") as mock_run:
            # Mock successful git pull for all repos
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Already up to date.\n",
                stderr="",
            )

            result = runner.invoke(app, ["pull", "-g", "pymongo"])

            assert result.exit_code == 0
            output = strip_ansi(result.stdout)
            assert "Pulling 2 repository(ies) in group 'pymongo'" in output
            assert "Done! Pulled 2 repository(ies)" in output


def test_pull_repo_not_found(temp_repos_dir, mock_config):
    """Test pulling a repository that doesn't exist."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        result = runner.invoke(app, ["pull", "nonexistent-repo"])

        assert result.exit_code == 1
        # Error messages go to stderr
        output = strip_ansi(result.stderr)
        assert "Repository 'nonexistent-repo' not found" in output


def test_pull_group_not_found(temp_repos_dir, mock_config):
    """Test pulling a group that doesn't exist."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        result = runner.invoke(app, ["pull", "-g", "nonexistent-group"])

        assert result.exit_code == 1
        # Error messages go to stderr
        output = strip_ansi(result.stderr)
        assert "Group 'nonexistent-group' not found" in output


def test_pull_no_args(temp_repos_dir, mock_config):
    """Test pull command with no arguments."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        result = runner.invoke(app, ["pull"])

        # Exit code 2 is from typer when no_args_is_help=True
        assert result.exit_code == 2
        output = strip_ansi(result.stdout)
        # With no_args_is_help=True, it shows help instead of error
        assert "Pull updates from remote repositories" in output or "Usage:" in output


def test_pull_list_repos(temp_repos_dir, mock_config):
    """Test listing repositories with --list flag."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        result = runner.invoke(app, ["pull", "--list"])

        assert result.exit_code == 0
        output = strip_ansi(result.stdout)
        assert "Repository status" in output
        assert "pymongo" in output
        assert "django" in output


def test_pull_failed(temp_repos_dir, mock_config):
    """Test pulling a repository that fails."""
    with patch("dbx_python_cli.commands.pull.get_config", return_value=mock_config):
        with patch("subprocess.run") as mock_run:
            # Mock failed git pull
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="error: Your local changes would be overwritten by merge.\n",
            )

            result = runner.invoke(app, ["pull", "mongo-python-driver"])

            assert result.exit_code == 0  # Command itself succeeds, but git pull fails
            # Error output goes to stderr
            output = strip_ansi(result.stderr)
            assert "mongo-python-driver: git pull failed" in output
            assert "Your local changes would be overwritten" in output
