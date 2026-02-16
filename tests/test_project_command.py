"""Tests for the project command."""

import re

from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


def strip_ansi(text):
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def test_project_help():
    """Test that the project help command works."""
    result = runner.invoke(app, ["project", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "Project management commands" in output


def test_project_add_help():
    """Test that the project add help command works."""
    result = runner.invoke(app, ["project", "add", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "Create a new Django project using bundled templates" in output
    assert "--add-frontend" in output
    assert "--base-dir" in output


def test_project_remove_help():
    """Test that the project remove help command works."""
    result = runner.invoke(app, ["project", "remove", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "Delete a Django project by name" in output


def test_project_add_no_name_no_random():
    """Test that project add generates a random name when no name is provided."""
    # When no name is provided, a random name is automatically generated
    # This test just verifies the help text mentions this behavior
    result = runner.invoke(app, ["project", "add", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    # Check that the help text mentions random name generation
    assert "random name" in output.lower()


def test_project_edit_help():
    """Test that the project edit help command works."""
    result = runner.invoke(app, ["project", "edit", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "Edit project settings file with your default editor" in output
    assert "--settings" in output
    assert "--directory" in output
