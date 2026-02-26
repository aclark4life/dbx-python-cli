"""Tests for the clone command."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dbx_python_cli.cli import app

runner = CliRunner()


def _make_config(tmp_path, global_groups=None, extra_groups=None):
    """Build a minimal config dict for clone tests."""
    groups = {}
    if global_groups:
        for gname, urls in global_groups.items():
            groups[gname] = {"repos": urls}
    if extra_groups:
        for gname, urls in extra_groups.items():
            groups[gname] = {"repos": urls}
    config = {
        "repo": {
            "base_dir": str(tmp_path),
            "groups": groups,
        }
    }
    if global_groups:
        config["repo"]["global_groups"] = list(global_groups.keys())
    return config


# ---------------------------------------------------------------------------
# Basic clone tests
# ---------------------------------------------------------------------------


def test_clone_no_args_shows_error():
    """Test that clone with no arguments shows an error."""
    with patch("dbx_python_cli.commands.clone.repo.get_config", return_value={}):
        result = runner.invoke(app, ["clone"])
        assert result.exit_code != 0


def test_clone_nonexistent_group(tmp_path):
    """Test that cloning a nonexistent group shows an error."""
    config = _make_config(
        tmp_path,
        extra_groups={"pymongo": ["git@github.com:mongodb/specifications.git"]},
    )
    with patch("dbx_python_cli.commands.clone.repo.get_config", return_value=config):
        result = runner.invoke(app, ["clone", "-g", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.stdout or "not found" in (result.stderr or "")


# ---------------------------------------------------------------------------
# Global group injection tests
# ---------------------------------------------------------------------------


def test_clone_group_includes_global_repos(tmp_path):
    """When cloning a group, global repos are also cloned into the same directory."""
    config = _make_config(
        tmp_path,
        global_groups={"global": ["git@github.com:mongodb/mongo-python-driver.git"]},
        extra_groups={
            "django": ["git@github.com:mongodb-labs/django-mongodb-backend.git"]
        },
    )

    with patch("dbx_python_cli.commands.clone.repo.get_config", return_value=config):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = runner.invoke(app, ["clone", "-g", "django", "--no-install"])
            assert result.exit_code == 0

            # Collect all git clone calls
            clone_calls = [
                c
                for c in mock_run.call_args_list
                if c.args and c.args[0][:2] == ["git", "clone"]
            ]
            cloned_urls = [c.args[0][2] for c in clone_calls]

            assert any("django-mongodb-backend" in url for url in cloned_urls)
            assert any("mongo-python-driver" in url for url in cloned_urls)


def test_clone_group_global_repos_cloned_into_target_dir(tmp_path):
    """Global repos are cloned into the target group directory, not a 'global/' dir."""
    config = _make_config(
        tmp_path,
        global_groups={"global": ["git@github.com:mongodb/mongo-python-driver.git"]},
        extra_groups={"pymongo": ["git@github.com:mongodb/specifications.git"]},
    )

    with patch("dbx_python_cli.commands.clone.repo.get_config", return_value=config):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            runner.invoke(app, ["clone", "-g", "pymongo", "--no-install"])

            clone_calls = [
                c
                for c in mock_run.call_args_list
                if c.args and c.args[0][:2] == ["git", "clone"]
            ]
            # The destination paths (4th argument) should all be inside pymongo/
            dest_paths = [c.args[0][3] for c in clone_calls]
            assert all(str(tmp_path / "pymongo") in p for p in dest_paths), (
                f"Expected all clones in pymongo/, got: {dest_paths}"
            )


def test_clone_group_no_global_groups_configured(tmp_path):
    """When no global_groups are configured, only the target group is cloned."""
    config = _make_config(
        tmp_path,
        extra_groups={"pymongo": ["git@github.com:mongodb/specifications.git"]},
    )

    with patch("dbx_python_cli.commands.clone.repo.get_config", return_value=config):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            runner.invoke(app, ["clone", "-g", "pymongo", "--no-install"])

            clone_calls = [
                c
                for c in mock_run.call_args_list
                if c.args and c.args[0][:2] == ["git", "clone"]
            ]
            assert len(clone_calls) == 1
            assert "specifications" in clone_calls[0].args[0][2]


def test_clone_global_group_itself_not_doubled(tmp_path):
    """Cloning the global group itself does not duplicate global repos."""
    config = _make_config(
        tmp_path,
        global_groups={"global": ["git@github.com:mongodb/mongo-python-driver.git"]},
    )

    with patch("dbx_python_cli.commands.clone.repo.get_config", return_value=config):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            runner.invoke(app, ["clone", "-g", "global", "--no-install"])

            clone_calls = [
                c
                for c in mock_run.call_args_list
                if c.args and c.args[0][:2] == ["git", "clone"]
            ]
            # Should clone mongo-python-driver exactly once
            mpd_calls = [
                c for c in clone_calls if "mongo-python-driver" in c.args[0][2]
            ]
            assert len(mpd_calls) == 1
