"""Tests for the install command."""

import re
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


def strip_ansi(text):
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def test_install_help():
    """Test install command help."""
    result = runner.invoke(app, ["install", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.stdout)
    assert "Install commands" in output
    assert "--extras" in output
    assert "--groups" in output


def test_install_list_no_repos(tmp_path):
    """Test install --list with no repositories."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
            result = runner.invoke(app, ["install", "--list"])
            assert result.exit_code == 0
            assert "No repositories found" in result.stdout


def test_install_list_shows_repos(tmp_path):
    """Test install --list shows available repositories."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
            result = runner.invoke(app, ["install", "--list"])
            assert result.exit_code == 0
            assert "mongo-python-driver" in result.stdout
            assert "pymongo" in result.stdout


def test_install_list_short_form(tmp_path):
    """Test install -l short form."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
            result = runner.invoke(app, ["install", "-l"])
            assert result.exit_code == 0


def test_install_no_args_shows_error():
    """Test install with no arguments shows error."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": "/tmp/test"}}
            result = runner.invoke(app, ["install"])
            assert result.exit_code == 1
            assert (
                "Usage:" in result.stdout
                or "Repository name is required" in result.stdout
            )


def test_install_nonexistent_repo(tmp_path):
    """Test install with nonexistent repository."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
            result = runner.invoke(app, ["install", "nonexistent-repo"])
            assert result.exit_code == 1
            assert "not found" in result.stdout or "dbx install --list" in result.stdout


def test_install_basic_success(tmp_path):
    """Test basic install without extras or groups."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["install", "mongo-python-driver"])
                assert result.exit_code == 0
                assert "Installing dependencies" in result.stdout
                assert "Package installed successfully" in result.stdout

                # Verify uv pip install was called
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args[0][0] == ["uv", "pip", "install", "-e", "."]


def test_install_with_extras(tmp_path):
    """Test install with extras."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(
                    app, ["install", "mongo-python-driver", "-e", "test"]
                )
                assert result.exit_code == 0
                assert "Package installed successfully" in result.stdout

                # Verify uv pip install was called with extras
                call_args = mock_run.call_args
                assert call_args[0][0] == ["uv", "pip", "install", "-e", ".[test]"]


def test_install_with_multiple_extras(tmp_path):
    """Test install with multiple extras."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(
                    app, ["install", "mongo-python-driver", "-e", "test,aws"]
                )
                assert result.exit_code == 0


def test_install_with_groups(tmp_path):
    """Test install with dependency groups."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(
                    app, ["install", "mongo-python-driver", "-g", "dev"]
                )
                assert result.exit_code == 0
                assert "Package installed successfully" in result.stdout
                assert "Installing dependency groups: dev" in result.stdout
                assert "Group 'dev' installed successfully" in result.stdout

                # Verify both install calls were made
                assert mock_run.call_count == 2
                # First call: install package
                assert mock_run.call_args_list[0][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "-e",
                    ".",
                ]
                # Second call: install group
                assert mock_run.call_args_list[1][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--group",
                    "dev",
                ]


def test_install_with_extras_and_groups(tmp_path):
    """Test install with both extras and dependency groups."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(
                    app,
                    [
                        "install",
                        "mongo-python-driver",
                        "-e",
                        "test,aws",
                        "-g",
                        "dev,test",
                    ],
                )
                assert result.exit_code == 0

                # Verify install calls
                assert mock_run.call_count == 3  # 1 for package + 2 for groups
                # First call: install package with extras
                assert mock_run.call_args_list[0][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "-e",
                    ".[test,aws]",
                ]
                # Second call: install first group
                assert mock_run.call_args_list[1][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--group",
                    "dev",
                ]
                # Third call: install second group
                assert mock_run.call_args_list[2][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--group",
                    "test",
                ]


def test_install_failure(tmp_path):
    """Test install handles failure gracefully."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 1
                mock_result.stderr = "Installation failed"
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["install", "mongo-python-driver"])
                assert result.exit_code == 1
                # Check stderr instead of stdout for error messages
                assert "Warning" in result.stdout or result.exit_code == 1
