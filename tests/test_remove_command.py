"""Tests for the remove command module."""

import re
from unittest.mock import patch

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
    """Mock configuration."""
    return {
        "repo": {
            "base_dir": str(temp_repos_dir),
            "groups": {
                "pymongo": {
                    "repos": [
                        "https://github.com/mongodb/mongo-python-driver.git",
                        "https://github.com/mongodb/specifications.git",
                    ]
                },
                "django": {
                    "repos": [
                        "https://github.com/mongodb-labs/django-mongodb-backend.git",
                    ]
                },
                "langchain": {
                    "repos": [
                        "https://github.com/langchain-ai/langchain-mongodb.git",
                    ]
                },
            },
        }
    }


def test_remove_list_groups(mock_config):
    """Test listing available groups."""
    with patch("dbx_python_cli.cli.repo.get_config", return_value=mock_config):
        result = runner.invoke(app, ["remove", "--list"])
        assert result.exit_code == 0
        output = strip_ansi(result.stdout)
        assert "Available groups:" in output
        assert "pymongo (cloned)" in output
        assert "django (cloned)" in output
        assert "langchain (not cloned)" in output


def test_remove_group_with_confirmation_no(mock_config, temp_repos_dir):
    """Test removing a group with confirmation declined."""
    with patch("dbx_python_cli.cli.repo.get_config", return_value=mock_config):
        # Simulate user saying "no" to confirmation
        result = runner.invoke(app, ["remove", "pymongo"], input="n\n")
        assert result.exit_code == 0
        output = strip_ansi(result.stdout)
        assert "Removal cancelled" in output
        # Verify directory still exists
        assert (temp_repos_dir / "pymongo").exists()


def test_remove_group_with_force(mock_config, temp_repos_dir):
    """Test removing a group with --force flag."""
    with patch("dbx_python_cli.cli.repo.get_config", return_value=mock_config):
        result = runner.invoke(app, ["remove", "pymongo", "--force"])
        assert result.exit_code == 0
        output = strip_ansi(result.stdout)
        assert "Successfully removed 'pymongo' group directory" in output
        assert "Removed 2 repository(ies)" in output
        # Verify directory was removed
        assert not (temp_repos_dir / "pymongo").exists()


def test_remove_group_with_confirmation_yes(mock_config, temp_repos_dir):
    """Test removing a group with confirmation accepted."""
    with patch("dbx_python_cli.cli.repo.get_config", return_value=mock_config):
        # Simulate user saying "yes" to confirmation
        result = runner.invoke(app, ["remove", "django"], input="y\n")
        assert result.exit_code == 0
        output = strip_ansi(result.stdout)
        assert "Successfully removed 'django' group directory" in output
        # Verify directory was removed
        assert not (temp_repos_dir / "django").exists()


def test_remove_nonexistent_group(mock_config):
    """Test removing a non-existent group."""
    with patch("dbx_python_cli.cli.repo.get_config", return_value=mock_config):
        result = runner.invoke(app, ["remove", "nonexistent"])
        assert result.exit_code == 1
        # Error messages go to stdout when using typer.echo(..., err=True)
        # but the helpful message goes to stdout
        output = strip_ansi(result.stdout)
        assert "dbx remove --list" in output


def test_remove_no_group_name(mock_config):
    """Test remove command without group name."""
    with patch("dbx_python_cli.cli.repo.get_config", return_value=mock_config):
        result = runner.invoke(app, ["remove"])
        assert result.exit_code == 1
        # Error messages go to stdout when using typer.echo(..., err=True)
        # but the usage message goes to stdout
        output = strip_ansi(result.stdout)
        assert "dbx remove <group_name>" in output or "dbx remove --list" in output

