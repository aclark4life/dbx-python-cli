"""Tests for the CLI module."""

from typer.testing import CliRunner

from dbx.cli import app

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

