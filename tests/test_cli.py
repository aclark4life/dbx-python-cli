"""Tests for the CLI module."""

from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


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
    assert "--verbose" in result.stdout
    assert "-v" in result.stdout
    assert "Show more detailed output" in result.stdout


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
