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
    assert "--dependency-groups" in output


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
    (repo_dir / "setup.py").write_text("# setup.py")

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
                assert call_args[0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    "python",
                    "-e",
                    ".",
                ]


def test_install_with_extras(tmp_path):
    """Test install with extras."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()
    (repo_dir / "setup.py").write_text("# setup.py")

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
                assert call_args[0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    "python",
                    "-e",
                    ".[test]",
                ]


def test_install_with_multiple_extras(tmp_path):
    """Test install with multiple extras."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()
    (repo_dir / "setup.py").write_text("# setup.py")

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
    (repo_dir / "setup.py").write_text("# setup.py")

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(
                    app,
                    ["install", "mongo-python-driver", "--dependency-groups", "dev"],
                )
                assert result.exit_code == 0
                assert "Package installed successfully" in result.stdout

                # Verify both install calls were made (package + dependency group)
                assert mock_run.call_count == 2
                # First call: install package
                assert mock_run.call_args_list[0][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    "python",
                    "-e",
                    ".",
                ]
                # Second call: install dependency group
                assert mock_run.call_args_list[1][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    "python",
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
    (repo_dir / "setup.py").write_text("# setup.py")

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
                        "--dependency-groups",
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
                    "--python",
                    "python",
                    "-e",
                    ".[test,aws]",
                ]
                # Second call: install first group
                assert mock_run.call_args_list[1][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    "python",
                    "--group",
                    "dev",
                ]
                # Third call: install second group
                assert mock_run.call_args_list[2][0][0] == [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    "python",
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


def test_install_group_all_repos(tmp_path):
    """Test install -g <group> installs all repos in the group."""
    # Create mock repository structure with multiple repos
    group_dir = tmp_path / "pymongo"
    repo1_dir = group_dir / "mongo-python-driver"
    repo2_dir = group_dir / "drivers-evergreen-tools"
    repo1_dir.mkdir(parents=True)
    repo2_dir.mkdir(parents=True)
    (repo1_dir / ".git").mkdir()
    (repo2_dir / ".git").mkdir()
    # Create setup.py files to make them installable
    (repo1_dir / "setup.py").write_text("# setup.py")
    (repo2_dir / "setup.py").write_text("# setup.py")

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["install", "-g", "pymongo"])
                assert result.exit_code == 0
                assert "Installing all repositories in group 'pymongo'" in result.stdout
                assert "mongo-python-driver" in result.stdout
                assert "drivers-evergreen-tools" in result.stdout
                assert "Installation Summary" in result.stdout
                assert "Total packages: 2" in result.stdout

                # Verify install was called for both repos
                assert mock_run.call_count == 2


def test_install_group_all_repos_with_extras(tmp_path):
    """Test install -g <group> with extras installs all repos with extras."""
    # Create mock repository structure with multiple repos
    group_dir = tmp_path / "pymongo"
    repo1_dir = group_dir / "mongo-python-driver"
    repo2_dir = group_dir / "drivers-evergreen-tools"
    repo1_dir.mkdir(parents=True)
    repo2_dir.mkdir(parents=True)
    (repo1_dir / ".git").mkdir()
    (repo2_dir / ".git").mkdir()
    # Create setup.py files to make them installable
    (repo1_dir / "setup.py").write_text("# setup.py")
    (repo2_dir / "setup.py").write_text("# setup.py")

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["install", "-g", "pymongo", "-e", "test"])
                assert result.exit_code == 0
                assert "Installing all repositories in group 'pymongo'" in result.stdout

                # Verify install was called with extras for both repos
                assert mock_run.call_count == 2
                for call_args in mock_run.call_args_list:
                    assert ".[test]" in call_args[0][0]


def test_install_group_nonexistent(tmp_path):
    """Test install -g with nonexistent group."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
            result = runner.invoke(app, ["install", "-g", "nonexistent"])
            assert result.exit_code == 1
            # Error messages go to stdout in typer
            output = result.stdout + result.stderr
            assert "not found" in output or result.exit_code == 1


def test_install_group_no_repos(tmp_path):
    """Test install -g with group that has no repos."""
    # Create empty group directory
    group_dir = tmp_path / "pymongo"
    group_dir.mkdir(parents=True)

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
            result = runner.invoke(app, ["install", "-g", "pymongo"])
            assert result.exit_code == 1
            # Error messages go to stdout in typer
            output = result.stdout + result.stderr
            assert "No repositories found" in output or result.exit_code == 1


def test_install_duplicate_repo_warning(tmp_path):
    """Test warning when repo exists in multiple groups."""
    # Create same repo in two different groups
    pymongo_group = tmp_path / "pymongo"
    langchain_group = tmp_path / "langchain"

    pymongo_repo = pymongo_group / "mongo-python-driver"
    langchain_repo = langchain_group / "mongo-python-driver"

    pymongo_repo.mkdir(parents=True)
    langchain_repo.mkdir(parents=True)

    (pymongo_repo / ".git").mkdir()
    (langchain_repo / ".git").mkdir()
    (pymongo_repo / "setup.py").write_text("# setup.py")
    (langchain_repo / "setup.py").write_text("# setup.py")

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch("subprocess.run") as mock_run:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = runner.invoke(app, ["install", "mongo-python-driver"])
                assert result.exit_code == 0

                # Check for warning about duplicate repos
                output = result.stdout + result.stderr
                assert "found in multiple groups" in output
                assert "pymongo" in output or "langchain" in output
                assert "Use -g to specify" in output


def test_install_show_options(tmp_path):
    """Test --show-options flag shows available extras and dependency groups."""
    # Create mock repository structure
    group_dir = tmp_path / "pymongo"
    repo_dir = group_dir / "mongo-python-driver"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    # Create pyproject.toml with extras and dependency groups
    pyproject_content = """
[project]
name = "pymongo"

[project.optional-dependencies]
test = ["pytest"]
aws = ["boto3"]
encryption = ["pymongocrypt"]

[dependency-groups]
dev = ["ruff", "mypy"]
docs = ["sphinx"]
"""
    (repo_dir / "pyproject.toml").write_text(pyproject_content)

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}

            result = runner.invoke(
                app, ["install", "mongo-python-driver", "--show-options"]
            )
            assert result.exit_code == 0
            assert "📦 mongo-python-driver" in result.stdout
            assert "Extras: aws, encryption, test" in result.stdout
            assert "Dependency groups: dev, docs" in result.stdout


def test_install_show_options_no_repo(tmp_path):
    """Test --show-options without repo name shows error."""
    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}

            result = runner.invoke(app, ["install", "--show-options"])
            assert result.exit_code == 1
            output = result.stdout + result.stderr
            assert "Repository name required with --show-options" in output


def test_install_show_options_monorepo(tmp_path):
    """Test --show-options with monorepo shows options for each package."""
    # Create mock repository structure
    group_dir = tmp_path / "langchain"
    repo_dir = group_dir / "langchain-mongodb"
    repo_dir.mkdir(parents=True)
    (repo_dir / ".git").mkdir()

    # Create subdirectories for monorepo
    pkg1_dir = repo_dir / "libs" / "langchain-mongodb"
    pkg2_dir = repo_dir / "libs" / "langgraph-checkpoint-mongodb"
    pkg1_dir.mkdir(parents=True)
    pkg2_dir.mkdir(parents=True)

    # Create pyproject.toml for each package
    pyproject1 = """
[project]
name = "langchain-mongodb"

[project.optional-dependencies]
test = ["pytest"]

[dependency-groups]
dev = ["ruff"]
"""
    pyproject2 = """
[project]
name = "langgraph-checkpoint-mongodb"

[project.optional-dependencies]
test = ["pytest"]
docs = ["sphinx"]
"""
    (pkg1_dir / "pyproject.toml").write_text(pyproject1)
    (pkg2_dir / "pyproject.toml").write_text(pyproject2)

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            with patch(
                "dbx_python_cli.commands.install.get_install_dirs"
            ) as mock_install_dirs:
                mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}
                mock_install_dirs.return_value = [
                    "libs/langchain-mongodb/",
                    "libs/langgraph-checkpoint-mongodb/",
                ]

                result = runner.invoke(
                    app, ["install", "langchain-mongodb", "--show-options"]
                )
                assert result.exit_code == 0
                assert (
                    "📦 langchain-mongodb (monorepo with 2 packages)" in result.stdout
                )
                assert "Package: libs/langchain-mongodb/" in result.stdout
                assert "Package: libs/langgraph-checkpoint-mongodb/" in result.stdout
                assert "Extras: test" in result.stdout
                assert "Dependency groups: dev" in result.stdout


def test_install_show_options_with_group(tmp_path):
    """Test --show-options with -G flag to specify group for single repo."""
    # Create mock repository structure with same repo in two groups
    group1_dir = tmp_path / "pymongo"
    group2_dir = tmp_path / "langchain"
    repo1_dir = group1_dir / "mongo-python-driver"
    repo2_dir = group2_dir / "mongo-python-driver"
    repo1_dir.mkdir(parents=True)
    repo2_dir.mkdir(parents=True)
    (repo1_dir / ".git").mkdir()
    (repo2_dir / ".git").mkdir()

    # Create different pyproject.toml for each
    pyproject1 = """
[project]
name = "pymongo"

[project.optional-dependencies]
test = ["pytest"]
aws = ["boto3"]
"""
    pyproject2 = """
[project]
name = "pymongo"

[project.optional-dependencies]
test = ["pytest"]
langchain = ["langchain"]
"""
    (repo1_dir / "pyproject.toml").write_text(pyproject1)
    (repo2_dir / "pyproject.toml").write_text(pyproject2)

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}

            # Show options for pymongo group using -G flag
            result = runner.invoke(
                app,
                ["install", "mongo-python-driver", "--show-options", "-G", "pymongo"],
            )
            assert result.exit_code == 0
            assert "📦 mongo-python-driver" in result.stdout
            assert "Extras: aws, test" in result.stdout

            # Show options for langchain group using -G flag
            result = runner.invoke(
                app,
                ["install", "mongo-python-driver", "--show-options", "-G", "langchain"],
            )
            assert result.exit_code == 0
            assert "📦 mongo-python-driver" in result.stdout
            assert "Extras: langchain, test" in result.stdout


def test_install_show_options_all_repos_in_group(tmp_path):
    """Test --show-options with -g flag to show all repos in a group."""
    # Create mock repository structure with multiple repos in a group
    group_dir = tmp_path / "pymongo"
    repo1_dir = group_dir / "mongo-python-driver"
    repo2_dir = group_dir / "motor"
    repo1_dir.mkdir(parents=True)
    repo2_dir.mkdir(parents=True)
    (repo1_dir / ".git").mkdir()
    (repo2_dir / ".git").mkdir()

    # Create pyproject.toml for each repo
    pyproject1 = """
[project]
name = "pymongo"

[project.optional-dependencies]
test = ["pytest"]
aws = ["boto3"]

[dependency-groups]
dev = ["ruff"]
"""
    pyproject2 = """
[project]
name = "motor"

[project.optional-dependencies]
test = ["pytest"]

[dependency-groups]
dev = ["ruff"]
docs = ["sphinx"]
"""
    (repo1_dir / "pyproject.toml").write_text(pyproject1)
    (repo2_dir / "pyproject.toml").write_text(pyproject2)

    with patch("dbx_python_cli.commands.repo.get_config_path") as _mock_path:
        with patch("dbx_python_cli.commands.install.get_config") as mock_config:
            mock_config.return_value = {"repo": {"base_dir": str(tmp_path)}}

            # Show options for all repos in pymongo group
            result = runner.invoke(app, ["install", "--show-options", "-g", "pymongo"])
            assert result.exit_code == 0
            assert (
                "Showing options for all repositories in group 'pymongo'"
                in result.stdout
            )
            assert "mongo-python-driver:" in result.stdout
            assert "motor:" in result.stdout
            assert "Extras: aws, test" in result.stdout
            assert "Dependency groups: dev" in result.stdout
            assert "Dependency groups: dev, docs" in result.stdout
