"""Tests for the CLI module."""

import re

from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


def strip_ansi(text):
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def test_app_help():
    """Test that the CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "A command line tool for DBX Python development tasks" in result.stdout


def test_app_version():
    """Test that the CLI version command works."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "dbx, version 0.1.0" in result.stdout


def test_app_no_args():
    """Test that the CLI shows help when run without arguments."""
    result = runner.invoke(app, [])
    # Typer returns exit code 2 when no command is provided (shows help)
    assert result.exit_code == 2


def test_verbose_flag_in_help():
    """Test that the verbose flag appears in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "--verbose" in output
    assert "-v" in output
    assert "Show more detailed output" in output


def test_verbose_flag_with_test_command():
    """Test that verbose flag works with test command."""
    from unittest.mock import patch

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.test.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": "/tmp/test"}}
            result = runner.invoke(app, ["-v", "test", "--list"])
            assert result.exit_code == 0
            assert "[verbose]" in result.stdout


def test_verbose_flag_with_install_command():
    """Test that verbose flag works with install command."""
    from unittest.mock import patch

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": "/tmp/test"}}
            result = runner.invoke(app, ["-v", "install", "--list"])
            assert result.exit_code == 0
            assert "[verbose]" in result.stdout


def test_list_flag_no_repos():
    """Test that the -l flag shows message when no repos are cloned."""
    from unittest.mock import patch

    with patch("dbx_python_cli.commands.repo.get_config") as mock_config:
        with patch("dbx_python_cli.commands.repo.find_all_repos") as mock_find:
            mock_config.return_value = {"repo": {"base_dir": "/tmp/test"}}
            mock_find.return_value = []
            result = runner.invoke(app, ["-l"])
            assert result.exit_code == 0
            assert "No repositories found" in result.stdout
            assert "Base directory:" in result.stdout


def test_list_flag_with_repos():
    """Test that the -l flag lists all cloned repositories."""
    from unittest.mock import patch

    with patch("dbx_python_cli.commands.repo.get_config") as mock_config:
        with patch("dbx_python_cli.commands.repo.find_all_repos") as mock_find:
            mock_config.return_value = {"repo": {"base_dir": "/tmp/test"}}
            mock_find.return_value = [
                {"group": "django", "name": "django"},
                {"group": "pymongo", "name": "mongo-python-driver"},
            ]
            result = runner.invoke(app, ["-l"])
            assert result.exit_code == 0
            assert "Repository status:" in result.stdout
            # Check for tree format
            assert "django/" in result.stdout
            assert "pymongo/" in result.stdout
            assert "django" in result.stdout
            assert "mongo-python-driver" in result.stdout
            assert "├──" in result.stdout or "└──" in result.stdout
            # Check for legend
            assert "Legend:" in result.stdout


def test_list_flag_short_form():
    """Test that the -l short form works."""
    from unittest.mock import patch

    with patch("dbx_python_cli.commands.repo.get_config") as mock_config:
        with patch("dbx_python_cli.commands.repo.find_all_repos") as mock_find:
            mock_config.return_value = {"repo": {"base_dir": "/tmp/test"}}
            mock_find.return_value = []
            result = runner.invoke(app, ["-l"])
            assert result.exit_code == 0
            assert "No repositories found" in result.stdout


def test_list_flag_in_help():
    """Test that the -l flag appears in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "--list" in output
    assert "-l" in output
    assert "Show repository status" in output
