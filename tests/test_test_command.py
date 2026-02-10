"""Tests for the test command module."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


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

    repo3 = django_dir / "django"
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
    "https://github.com/django/django.git",
]
"""
    config_path.write_text(config_content)
    return config_path


def test_test_help():
    """Test that the test help command works."""
    result = runner.invoke(app, ["test", "--help"])
    assert result.exit_code == 0
    assert "Test commands" in result.stdout


def test_test_list_no_repos(tmp_path):
    """Test that test --list shows message when no repos exist."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with patch("dbx_python_cli.commands.test.get_config") as mock_get_config:
        mock_get_config.return_value = {"repo": {"base_dir": str(empty_dir)}}

        result = runner.invoke(app, ["test", "--list"])
        # Exit code can be 0 or 1 depending on how typer.Exit is handled
        assert "No repositories found" in result.stdout


def test_test_list_shows_repos(mock_config, temp_repos_dir):
    """Test that test --list shows all available repositories."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["test", "--list"])
        # Exit code can be 0 or 1 depending on how typer.Exit is handled
        assert "mongo-python-driver" in result.stdout
        assert "specifications" in result.stdout
        assert "django" in result.stdout
        assert "pymongo/" in result.stdout
        assert "django/" in result.stdout
        assert "Legend:" in result.stdout


def test_test_list_short_form(mock_config, temp_repos_dir):
    """Test that test -l works as shortcut for --list."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["test", "-l"])
        # Exit code can be 0 or 1 depending on how typer.Exit is handled
        assert "mongo-python-driver" in result.stdout
        assert "Legend:" in result.stdout


def test_test_no_args_shows_error():
    """Test that test without args shows help."""
    result = runner.invoke(app, ["test"])
    # Typer exits with code 2 when showing help due to no_args_is_help=True
    assert result.exit_code == 2
    # Should show help/usage
    output = result.stdout + result.stderr
    assert "Usage:" in output


def test_test_nonexistent_repo(mock_config, temp_repos_dir):
    """Test that test fails with nonexistent repository."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = mock_config

        result = runner.invoke(app, ["test", "nonexistent-repo"])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Repository 'nonexistent-repo' not found" in output


def test_test_runs_pytest_success(mock_config, temp_repos_dir):
    """Test that test runs pytest successfully."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("dbx_python_cli.commands.test.get_venv_info") as mock_venv:
            with patch("subprocess.run") as mock_run:
                mock_get_path.return_value = mock_config
                mock_venv.return_value = ("python", "system")

                # Mock successful pytest run
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["test", "mongo-python-driver"])
                assert result.exit_code == 0
                assert "Running pytest" in result.stdout
                assert "Tests passed" in result.stdout

                # Verify pytest was called with correct arguments
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args[0][0] == ["python", "-m", "pytest"]
                assert "mongo-python-driver" in str(call_args[1]["cwd"])


def test_test_runs_pytest_failure(mock_config, temp_repos_dir):
    """Test that test handles pytest failures."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("subprocess.run") as mock_run:
            mock_get_path.return_value = mock_config

            # Mock failed pytest run
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result

            result = runner.invoke(app, ["test", "mongo-python-driver"])
            assert result.exit_code == 1
            assert "Running pytest" in result.stdout
            output = result.stdout + result.stderr
            assert "Tests failed" in output


def test_test_list_base_dir_not_exists(tmp_path):
    """Test that test -l handles non-existent base directory gracefully."""
    from dbx_python_cli.commands.repo_utils import find_all_repos

    # Test find_all_repos directly with non-existent directory
    nonexistent_dir = tmp_path / "nonexistent_repos"
    repos = find_all_repos(nonexistent_dir)
    assert repos == []

    # Also test via CLI
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    repos_dir_str = str(nonexistent_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"
"""
    config_path.write_text(config_content)

    # test.py imports get_config from repo.py, so we need to patch repo.get_config_path
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path
        result = runner.invoke(app, ["test", "-l"])
        # Should exit with 0 when listing (even if no repos found)
        assert result.exit_code == 0
        assert "No repositories found" in result.stdout
        assert "Base directory:" in result.stdout


def test_test_with_custom_test_runner(tmp_path):
    """Test that test uses custom test runner when configured."""
    # Create temp repos directory
    repos_dir = tmp_path / "repos"
    repos_dir.mkdir(parents=True)

    # Create django group and repo
    django_dir = repos_dir / "django"
    django_dir.mkdir()

    django_repo = django_dir / "django"
    django_repo.mkdir()
    (django_repo / ".git").mkdir()

    # Create custom test runner script
    tests_dir = django_repo / "tests"
    tests_dir.mkdir()
    test_runner = tests_dir / "runtests.py"
    test_runner.write_text("# Custom test runner")

    # Create config with custom test runner
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"
    repos_dir_str = str(repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.django]
repos = [
    "https://github.com/django/django.git",
]

[repo.groups.django.test_runner]
django = "tests/runtests.py"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("dbx_python_cli.commands.test.get_venv_info") as mock_venv:
            with patch("subprocess.run") as mock_run:
                mock_get_path.return_value = config_path
                mock_venv.return_value = ("python", "system")

                # Mock successful test run
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["test", "django"])
                assert result.exit_code == 0
                assert "Running tests/runtests.py" in result.stdout
                assert "Tests passed" in result.stdout

                # Verify custom test runner was called
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert "runtests.py" in call_args[0][0][1]
                assert "django" in str(call_args[1]["cwd"])


def test_test_with_custom_test_runner_not_found(tmp_path):
    """Test that test fails when custom test runner doesn't exist."""
    # Create temp repos directory
    repos_dir = tmp_path / "repos"
    repos_dir.mkdir(parents=True)

    # Create django group and repo
    django_dir = repos_dir / "django"
    django_dir.mkdir()

    django_repo = django_dir / "django"
    django_repo.mkdir()
    (django_repo / ".git").mkdir()

    # Don't create the test runner script

    # Create config with custom test runner
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"
    repos_dir_str = str(repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.django]
repos = [
    "https://github.com/django/django.git",
]

[repo.groups.django.test_runner]
django = "tests/runtests.py"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("dbx_python_cli.commands.test.get_venv_info") as mock_venv:
            mock_get_path.return_value = config_path
            mock_venv.return_value = ("python", "system")

            result = runner.invoke(app, ["test", "django"])
            assert result.exit_code == 1
            output = result.stdout + result.stderr
            assert "Test runner not found" in output


def test_test_fallback_to_pytest_when_no_test_runner(mock_config, temp_repos_dir):
    """Test that test falls back to pytest when no custom test runner is configured."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("dbx_python_cli.commands.test.get_venv_info") as mock_venv:
            with patch("subprocess.run") as mock_run:
                mock_get_path.return_value = mock_config
                mock_venv.return_value = ("python", "system")

                # Mock successful pytest run
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["test", "django"])
                assert result.exit_code == 0
                assert "Running pytest" in result.stdout

                # Verify pytest was called (not custom runner)
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args[0][0] == ["python", "-m", "pytest"]


def test_test_with_custom_test_runner_and_args(tmp_path):
    """Test that test passes arguments to custom test runner."""
    # Create temp repos directory
    repos_dir = tmp_path / "repos"
    repos_dir.mkdir(parents=True)

    # Create django group and repo
    django_dir = repos_dir / "django"
    django_dir.mkdir()

    django_repo = django_dir / "django"
    django_repo.mkdir()
    (django_repo / ".git").mkdir()

    # Create custom test runner script
    tests_dir = django_repo / "tests"
    tests_dir.mkdir()
    test_runner = tests_dir / "runtests.py"
    test_runner.write_text("# Custom test runner")

    # Create config with custom test runner
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"
    repos_dir_str = str(repos_dir).replace("\\", "/")
    config_content = f"""
[repo]
base_dir = "{repos_dir_str}"

[repo.groups.django]
repos = [
    "https://github.com/django/django.git",
]

[repo.groups.django.test_runner]
django = "tests/runtests.py"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("dbx_python_cli.commands.test.get_venv_info") as mock_venv:
            with patch("subprocess.run") as mock_run:
                mock_get_path.return_value = config_path
                mock_venv.return_value = ("python", "system")

                # Mock successful test run
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(
                    app, ["test", "django", "--verbose", "--parallel"]
                )
                assert result.exit_code == 0
                assert "Running tests/runtests.py --verbose --parallel" in result.stdout

                # Verify custom test runner was called with args
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert "runtests.py" in call_args[0][0][1]
                assert "--verbose" in call_args[0][0]
                assert "--parallel" in call_args[0][0]


def test_test_with_pytest_and_args(mock_config, temp_repos_dir):
    """Test that test passes arguments to pytest."""
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("dbx_python_cli.commands.test.get_venv_info") as mock_venv:
            with patch("subprocess.run") as mock_run:
                mock_get_path.return_value = mock_config
                mock_venv.return_value = ("python", "system")

                # Mock successful pytest run
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(
                    app, ["test", "mongo-python-driver", "-x", "--tb=short"]
                )
                assert result.exit_code == 0
                assert "Running pytest -x --tb=short" in result.stdout

                # Verify pytest was called with args
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args[0][0] == ["python", "-m", "pytest", "-x", "--tb=short"]
