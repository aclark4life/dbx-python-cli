"""Tests for the remote command."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


def test_remote_help():
    """Test remote help message."""
    result = runner.invoke(app, ["remote", "--help"])
    assert result.exit_code == 0
    assert "Show git remotes" in result.stdout


def test_remote_no_repo_name(tmp_path):
    """Test remote without repo name shows error."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"
        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = []
"""
        (tmp_path / "config.toml").write_text(config_content)

        result = runner.invoke(app, ["remote"])
        # Typer exits with code 2 for missing arguments when no_args_is_help=True
        assert result.exit_code == 2


def test_remote_repo_not_found(tmp_path):
    """Test remote with non-existent repository."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"
        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = []
"""
        (tmp_path / "config.toml").write_text(config_content)

        result = runner.invoke(app, ["remote", "nonexistent-repo"])
        assert result.exit_code == 1
        # Check that helpful message is shown
        assert "dbx list" in result.stdout


def test_remote_basic(tmp_path):
    """Test basic remote command."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"

        # Create a test repo
        test_group = tmp_path / "test"
        test_group.mkdir()
        test_repo = test_group / "test-repo"
        test_repo.mkdir()
        (test_repo / ".git").mkdir()

        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = ["https://github.com/test/test-repo.git"]
"""
        (tmp_path / "config.toml").write_text(config_content)

        # Mock subprocess.run to simulate git remote output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "origin\nupstream\n"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["remote", "test-repo"])
            assert result.exit_code == 0
            assert "🔗 test-repo: Remotes" in result.stdout
            assert "origin" in result.stdout
            assert "upstream" in result.stdout

            # Verify git remote was called correctly
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["git", "remote"]
            assert str(call_args[1]["cwd"]) == str(test_repo)


def test_remote_verbose(tmp_path):
    """Test remote with verbose flag."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"

        # Create a test repo
        test_group = tmp_path / "test"
        test_group.mkdir()
        test_repo = test_group / "test-repo"
        test_repo.mkdir()
        (test_repo / ".git").mkdir()

        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = ["https://github.com/test/test-repo.git"]
"""
        (tmp_path / "config.toml").write_text(config_content)

        # Mock subprocess.run to simulate git remote -v output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "origin\tgit@github.com:test/test-repo.git (fetch)\norigin\tgit@github.com:test/test-repo.git (push)\n"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = runner.invoke(app, ["-v", "remote", "test-repo"])
            assert result.exit_code == 0
            assert "🔗 test-repo: Remotes (with URLs)" in result.stdout
            assert "git@github.com:test/test-repo.git" in result.stdout

            # Verify git remote -v was called
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["git", "remote", "-v"]


def test_remote_with_group(tmp_path):
    """Test remote with group flag."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"

        # Create test repos
        test_group = tmp_path / "test"
        test_group.mkdir()

        test_repo1 = test_group / "repo1"
        test_repo1.mkdir()
        (test_repo1 / ".git").mkdir()

        test_repo2 = test_group / "repo2"
        test_repo2.mkdir()
        (test_repo2 / ".git").mkdir()

        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = [
    "https://github.com/test/repo1.git",
    "https://github.com/test/repo2.git"
]
"""
        (tmp_path / "config.toml").write_text(config_content)

        # Mock subprocess.run to simulate git remote output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "origin\n"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = runner.invoke(app, ["remote", "-g", "test"])
            assert result.exit_code == 0
            assert (
                "Showing remotes for 2 repository(ies) in group 'test'" in result.stdout
            )
            assert "🔗 repo1: Remotes" in result.stdout
            assert "🔗 repo2: Remotes" in result.stdout


def test_remote_with_nonexistent_group(tmp_path):
    """Test remote with non-existent group."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"
        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = []
"""
        (tmp_path / "config.toml").write_text(config_content)

        result = runner.invoke(app, ["remote", "-g", "nonexistent"])
        assert result.exit_code == 1
        # Error messages may be in stdout or stderr
        output = result.stdout + result.stderr
        assert "Group 'nonexistent' not found" in output


def test_remote_not_git_repo(tmp_path):
    """Test remote on a directory that's not a git repository."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"

        # Create a test repo without .git
        test_group = tmp_path / "test"
        test_group.mkdir()
        test_repo = test_group / "test-repo"
        test_repo.mkdir()
        # Don't create .git directory

        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = ["https://github.com/test/test-repo.git"]
"""
        (tmp_path / "config.toml").write_text(config_content)

        # Mock find_repo_by_name to return the non-git repo
        with patch(
            "dbx_python_cli.commands.remote.find_repo_by_name",
            return_value={
                "name": "test-repo",
                "path": test_repo,
                "group": "test",
            },
        ):
            result = runner.invoke(app, ["remote", "test-repo"])
            assert result.exit_code == 0
            # Error messages may be in stdout or stderr
            output = result.stdout + result.stderr
            assert "⚠️  test-repo: Not a git repository (skipping)" in output


def test_remote_no_remotes_configured(tmp_path):
    """Test remote when repository has no remotes configured."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"

        # Create a test repo
        test_group = tmp_path / "test"
        test_group.mkdir()
        test_repo = test_group / "test-repo"
        test_repo.mkdir()
        (test_repo / ".git").mkdir()

        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = ["https://github.com/test/test-repo.git"]
"""
        (tmp_path / "config.toml").write_text(config_content)

        # Mock subprocess.run to simulate no remotes
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = runner.invoke(app, ["remote", "test-repo"])
            assert result.exit_code == 0
            assert "(no remotes configured)" in result.stdout


def test_remote_with_project(tmp_path):
    """Test remote with project flag."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = tmp_path / "config.toml"

        # Create a project
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        test_project = projects_dir / "test-project"
        test_project.mkdir()
        (test_project / ".git").mkdir()

        config_content = f"""[repo]
base_dir = "{tmp_path.as_posix()}"

[repo.groups.test]
repos = []
"""
        (tmp_path / "config.toml").write_text(config_content)

        # Mock subprocess.run to simulate git remote output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "origin\n"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = runner.invoke(app, ["remote", "-p", "test-project"])
            assert result.exit_code == 0
            assert "🔗 test-project: Remotes" in result.stdout
