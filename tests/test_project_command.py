"""Tests for the project command."""

import re
from unittest.mock import patch, MagicMock

import typer
import pytest
from typer.testing import CliRunner

from dbx_python_cli.cli import app
from dbx_python_cli.commands.project import ensure_mongodb

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


# Tests for ensure_mongodb function


class TestEnsureMongodb:
    """Tests for the ensure_mongodb helper function."""

    def test_mongodb_uri_from_environment(self):
        """Test that MONGODB_URI from environment is used when present."""
        env = {"MONGODB_URI": "mongodb://myhost:27017"}
        result = ensure_mongodb(env)
        assert result["MONGODB_URI"] == "mongodb://myhost:27017"

    def test_mongodb_uri_empty_string_triggers_fallback(self):
        """Test that empty MONGODB_URI triggers config/runner fallback."""
        env = {"MONGODB_URI": ""}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {
                "project": {"default_env": {"MONGODB_URI": "mongodb://config:27017"}}
            }
            result = ensure_mongodb(env)
            assert result["MONGODB_URI"] == "mongodb://config:27017"

    def test_mongodb_uri_from_config(self):
        """Test that MONGODB_URI from config is used when env not set."""
        env = {}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {
                "project": {
                    "default_env": {"MONGODB_URI": "mongodb://confighost:27017"}
                }
            }
            result = ensure_mongodb(env)
            assert result["MONGODB_URI"] == "mongodb://confighost:27017"

    def test_mongodb_runner_started_on_success(self):
        """Test that mongodb-runner is started when no URI is available."""
        env = {}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {"project": {"default_env": {}}}

            with patch("dbx_python_cli.commands.project.subprocess.run") as mock_run:
                # First call: which npx (success)
                # Second call: npx mongodb-runner start (success with URI in output)
                mock_run.side_effect = [
                    MagicMock(returncode=0),  # which npx
                    MagicMock(
                        returncode=0,
                        stdout="Server started at mongodb://127.0.0.1:52065/\n",
                        stderr="",
                    ),  # mongodb-runner start
                ]

                result = ensure_mongodb(env)
                assert result["MONGODB_URI"] == "mongodb://127.0.0.1:52065"
                assert mock_run.call_count == 2

    def test_mongodb_runner_fallback_uri_on_no_output(self):
        """Test that default URI is used when mongodb-runner output can't be parsed."""
        env = {}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {"project": {"default_env": {}}}

            with patch("dbx_python_cli.commands.project.subprocess.run") as mock_run:
                # mongodb-runner succeeds but no URI in output
                mock_run.side_effect = [
                    MagicMock(returncode=0),  # which npx
                    MagicMock(returncode=0, stdout="Started\n", stderr=""),
                ]

                result = ensure_mongodb(env)
                assert result["MONGODB_URI"] == "mongodb://localhost:27017"

    def test_mongodb_runner_failure_exits(self):
        """Test that mongodb-runner failure exits with 'no db running'."""
        env = {}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {"project": {"default_env": {}}}

            with patch("dbx_python_cli.commands.project.subprocess.run") as mock_run:
                # First call: which npx (success)
                # Second call: npx mongodb-runner start (failure)
                mock_run.side_effect = [
                    MagicMock(returncode=0),  # which npx
                    MagicMock(returncode=1, stderr="MongoDB failed to start"),
                ]

                with pytest.raises(typer.Exit) as exc_info:
                    ensure_mongodb(env)
                assert exc_info.value.exit_code == 1

    def test_npx_not_available_exits(self):
        """Test that missing npx exits with 'no db running'."""
        env = {}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {"project": {"default_env": {}}}

            with patch("dbx_python_cli.commands.project.subprocess.run") as mock_run:
                # which npx fails
                mock_run.return_value = MagicMock(returncode=1)

                with pytest.raises(typer.Exit) as exc_info:
                    ensure_mongodb(env)
                assert exc_info.value.exit_code == 1

    def test_mongodb_runner_timeout_exits(self):
        """Test that mongodb-runner timeout exits with 'no db running'."""
        import subprocess

        env = {}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {"project": {"default_env": {}}}

            with patch("dbx_python_cli.commands.project.subprocess.run") as mock_run:
                # First call: which npx (success)
                # Second call: timeout
                mock_run.side_effect = [
                    MagicMock(returncode=0),  # which npx
                    subprocess.TimeoutExpired(cmd="npx", timeout=120),
                ]

                with pytest.raises(typer.Exit) as exc_info:
                    ensure_mongodb(env)
                assert exc_info.value.exit_code == 1

    def test_npx_file_not_found_exits(self):
        """Test that FileNotFoundError exits with 'no db running'."""
        env = {}
        with patch("dbx_python_cli.commands.project.get_config") as mock_config:
            mock_config.return_value = {"project": {"default_env": {}}}

            with patch("dbx_python_cli.commands.project.subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError("npx not found")

                with pytest.raises(typer.Exit) as exc_info:
                    ensure_mongodb(env)
                assert exc_info.value.exit_code == 1
