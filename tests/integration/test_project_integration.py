"""Integration tests for project commands."""

from unittest.mock import patch

from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


def test_project_add_with_frontend(tmp_path):
    """Test creating a project with frontend."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["project", "add", "testproject"])
        assert result.exit_code == 0
        assert "Creating project: testproject" in result.stdout
        assert "Adding frontend" in result.stdout

        # Verify project structure
        project_path = base_dir / "projects" / "testproject"
        assert project_path.exists()
        assert (project_path / "manage.py").exists()
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "justfile").exists()
        assert (project_path / "testproject").is_dir()
        assert (project_path / "testproject" / "settings").is_dir()
        assert (project_path / "testproject" / "settings" / "base.py").exists()

        # Verify frontend
        frontend_path = project_path / "frontend"
        assert frontend_path.exists()
        assert (frontend_path / "package.json").exists()
        assert (frontend_path / "webpack").is_dir()


def test_project_add_without_frontend(tmp_path):
    """Test creating a project without frontend."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["project", "add", "nofrontend", "--no-frontend"])
        assert result.exit_code == 0
        assert "Creating project: nofrontend" in result.stdout

        # Verify project structure
        project_path = base_dir / "projects" / "nofrontend"
        assert project_path.exists()
        assert (project_path / "manage.py").exists()
        assert (project_path / "pyproject.toml").exists()

        # Verify no frontend
        frontend_path = project_path / "frontend"
        assert not frontend_path.exists()


def test_project_add_with_random_name(tmp_path):
    """Test creating a project with random name."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["project", "add", "--random"])
        assert result.exit_code == 0
        assert "Creating project:" in result.stdout

        # Verify a project was created
        projects_dir = base_dir / "projects"
        assert projects_dir.exists()
        project_dirs = list(projects_dir.iterdir())
        assert len(project_dirs) == 1
        assert project_dirs[0].is_dir()
        assert (project_dirs[0] / "manage.py").exists()


def test_project_add_custom_directory(tmp_path):
    """Test creating a project in a custom directory."""
    custom_dir = tmp_path / "custom_projects"
    custom_dir.mkdir()

    result = runner.invoke(
        app, ["project", "add", "customproject", "-d", str(custom_dir)]
    )
    assert result.exit_code == 0

    # Verify project in custom location
    project_path = custom_dir / "customproject"
    assert project_path.exists()
    assert (project_path / "manage.py").exists()


def test_project_add_with_settings(tmp_path):
    """Test creating a project with specific settings."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["project", "add", "qeproject", "--settings=qe"])
        assert result.exit_code == 0

        # Verify pyproject.toml has correct settings
        project_path = base_dir / "projects" / "qeproject"
        pyproject_content = (project_path / "pyproject.toml").read_text()
        assert "DJANGO_SETTINGS_MODULE" in pyproject_content
        assert "qeproject.settings.qe" in pyproject_content


def test_project_remove(tmp_path):
    """Test removing a project."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        # First create a project
        result = runner.invoke(app, ["project", "add", "removetest"])
        assert result.exit_code == 0

        project_path = base_dir / "projects" / "removetest"
        assert project_path.exists()

        # Now remove it
        result = runner.invoke(app, ["project", "remove", "removetest"])
        assert result.exit_code == 0
        assert "Removed project removetest" in result.stdout

        # Verify it's gone
        assert not project_path.exists()


def test_project_remove_nonexistent(tmp_path):
    """Test removing a project that doesn't exist."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["project", "remove", "nonexistent"])
        assert result.exit_code == 0
        assert "does not exist" in result.stdout or "does not exist" in result.stderr


def test_project_install_with_dbx_install(tmp_path):
    """Test that projects can be installed with dbx install command."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path_1:
        mock_get_path_1.return_value = config_path

        # Create a project
        result = runner.invoke(app, ["project", "add", "installtest", "--no-frontend"])
        assert result.exit_code == 0

    # Now test that it can be found by dbx install
    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path_2:
        mock_get_path_2.return_value = config_path

        # List should show the project
        result = runner.invoke(app, ["install", "--list"])
        assert result.exit_code == 0
        # The project should be listed (it's in projects group)
        assert "installtest" in result.stdout or "projects" in result.stdout


def test_project_with_frontend_structure(tmp_path):
    """Test that frontend has correct structure."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        result = runner.invoke(app, ["project", "add", "frontendtest"])
        assert result.exit_code == 0

        # Verify detailed frontend structure
        frontend_path = base_dir / "projects" / "frontendtest" / "frontend"
        assert (frontend_path / "package.json").exists()
        assert (frontend_path / "webpack").is_dir()
        assert (frontend_path / "src").is_dir()

        # Check package.json has content
        package_json = (frontend_path / "package.json").read_text()
        assert "name" in package_json
        assert "dependencies" in package_json or "devDependencies" in package_json


def test_project_list(tmp_path):
    """Test listing projects."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        # Test with no projects directory
        result = runner.invoke(app, ["project", "-l"])
        assert result.exit_code == 0
        assert (
            "No projects" in result.stdout
        )  # Could be "No projects directory found" or "No projects found"

        # Create a project with frontend
        result = runner.invoke(app, ["project", "add", "project1"])
        assert result.exit_code == 0

        # Create a project without frontend
        result = runner.invoke(app, ["project", "add", "project2", "--no-frontend"])
        assert result.exit_code == 0

        # List projects
        result = runner.invoke(app, ["project", "-l"])
        assert result.exit_code == 0
        assert "Found 2 project(s)" in result.stdout
        assert "project1" in result.stdout
        assert "project2" in result.stdout
        assert "🎨" in result.stdout  # Frontend marker should appear


def test_project_list_long_form(tmp_path):
    """Test listing projects with --list flag."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        # Create a project
        result = runner.invoke(app, ["project", "add", "testproject"])
        assert result.exit_code == 0

        # List with --list flag
        result = runner.invoke(app, ["project", "--list"])
        assert result.exit_code == 0
        assert "Found 1 project(s)" in result.stdout
        assert "testproject" in result.stdout


def test_project_run_settings_module(tmp_path):
    """Test that run command uses correct settings module."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    projects_dir = base_dir / "projects"
    projects_dir.mkdir(parents=True)
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    # Create a minimal project structure
    project_path = projects_dir / "testproject"
    project_path.mkdir()
    (project_path / "manage.py").write_text("# manage.py")

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        with patch("subprocess.Popen") as mock_popen:
            # Mock the subprocess to prevent actual server start
            mock_popen.return_value.poll.return_value = None

            mock_get_path.return_value = config_path

            # Test default settings (should use project name)
            result = runner.invoke(app, ["project", "run", "testproject"])
            # The command will fail because manage.py doesn't work, but we can check the output
            assert (
                "DJANGO_SETTINGS_MODULE=testproject.settings.testproject"
                in result.stdout
            )

            # Test with explicit settings
            result = runner.invoke(
                app, ["project", "run", "testproject", "--settings", "base"]
            )
            assert "DJANGO_SETTINGS_MODULE=testproject.settings.base" in result.stdout


def test_project_run_nonexistent(tmp_path):
    """Test running a nonexistent project."""
    config_dir = tmp_path / ".config" / "dbx-python-cli"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.toml"

    base_dir = tmp_path / "repos"
    base_dir_str = str(base_dir).replace("\\", "/")

    config_content = f"""[repo]
base_dir = "{base_dir_str}"
"""
    config_path.write_text(config_content)

    with patch("dbx_python_cli.commands.repo_utils.get_config_path") as mock_get_path:
        mock_get_path.return_value = config_path

        # Try to run a nonexistent project
        result = runner.invoke(app, ["project", "run", "nonexistent"])
        assert result.exit_code == 1
        # Error messages go to stdout in typer
        output = result.stdout + (result.stderr or "")
        assert "not found" in output.lower()
