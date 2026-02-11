"""Tests for the repo module utilities."""

from pathlib import Path

import pytest

from dbx_python_cli.commands.repo_utils import (
    _expand_env_var_value,
    find_all_repos,
    find_repo_by_name,
    get_test_env_vars,
    list_repos,
)


@pytest.fixture
def temp_repos_dir(tmp_path):
    """Create a temporary repos directory with test repos."""
    repos_dir = tmp_path / "repos"
    repos_dir.mkdir()

    # Create group directories with repos
    django_group = repos_dir / "django"
    django_group.mkdir()
    (django_group / "django").mkdir()
    (django_group / "django" / ".git").mkdir()
    (django_group / "django-mongodb-backend").mkdir()
    (django_group / "django-mongodb-backend" / ".git").mkdir()

    pymongo_group = repos_dir / "pymongo"
    pymongo_group.mkdir()
    (pymongo_group / "mongo-python-driver").mkdir()
    (pymongo_group / "mongo-python-driver" / ".git").mkdir()

    # Create a directory without .git (should be ignored)
    (pymongo_group / "not-a-repo").mkdir()

    # Create a file (should be ignored)
    (django_group / "README.md").write_text("test")

    return repos_dir


def test_find_all_repos_empty_dir(tmp_path):
    """Test find_all_repos with an empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    repos = find_all_repos(empty_dir)
    assert repos == []


def test_find_all_repos_nonexistent_dir(tmp_path):
    """Test find_all_repos with a nonexistent directory."""
    nonexistent = tmp_path / "nonexistent"

    repos = find_all_repos(nonexistent)
    assert repos == []


def test_find_all_repos_with_repos(temp_repos_dir):
    """Test find_all_repos with actual repos."""
    repos = find_all_repos(temp_repos_dir)

    assert len(repos) == 3
    repo_names = [r["name"] for r in repos]
    assert "django" in repo_names
    assert "django-mongodb-backend" in repo_names
    assert "mongo-python-driver" in repo_names
    assert "not-a-repo" not in repo_names  # No .git directory


def test_find_all_repos_structure(temp_repos_dir):
    """Test that find_all_repos returns correct structure."""
    repos = find_all_repos(temp_repos_dir)

    for repo in repos:
        assert "name" in repo
        assert "path" in repo
        assert "group" in repo
        assert isinstance(repo["path"], Path)


def test_find_all_repos_groups(temp_repos_dir):
    """Test that find_all_repos correctly identifies groups."""
    repos = find_all_repos(temp_repos_dir)

    django_repos = [r for r in repos if r["group"] == "django"]
    pymongo_repos = [r for r in repos if r["group"] == "pymongo"]

    assert len(django_repos) == 2
    assert len(pymongo_repos) == 1


def test_find_repo_by_name_found(temp_repos_dir):
    """Test find_repo_by_name when repo exists."""
    repo = find_repo_by_name("django", temp_repos_dir)

    assert repo is not None
    assert repo["name"] == "django"
    assert repo["group"] == "django"
    assert repo["path"] == temp_repos_dir / "django" / "django"


def test_find_repo_by_name_not_found(temp_repos_dir):
    """Test find_repo_by_name when repo doesn't exist."""
    repo = find_repo_by_name("nonexistent-repo", temp_repos_dir)

    assert repo is None


def test_find_repo_by_name_empty_dir(tmp_path):
    """Test find_repo_by_name with empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    repo = find_repo_by_name("any-repo", empty_dir)
    assert repo is None


def test_list_repos_empty(tmp_path):
    """Test list_repos with no repos."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = list_repos(empty_dir)
    assert result is None


def test_list_repos_default_format(temp_repos_dir):
    """Test list_repos with default format (tree structure)."""
    result = list_repos(temp_repos_dir, format_style="default")

    assert result is not None
    # Tree format should show groups as directories
    assert "django/" in result
    assert "pymongo/" in result
    # And repos under their groups
    assert "django" in result
    assert "django-mongodb-backend" in result
    assert "mongo-python-driver" in result
    # Should have tree characters
    assert "├──" in result or "└──" in result


def test_list_repos_grouped_format(temp_repos_dir):
    """Test list_repos with grouped format."""
    result = list_repos(temp_repos_dir, format_style="grouped")

    assert result is not None
    assert "[django]" in result
    assert "[pymongo]" in result
    assert "• django" in result
    assert "• django-mongodb-backend" in result
    assert "• mongo-python-driver" in result


def test_list_repos_simple_format(temp_repos_dir):
    """Test list_repos with simple format."""
    result = list_repos(temp_repos_dir, format_style="simple")

    assert result is not None
    assert "• django (django)" in result
    assert "• django-mongodb-backend (django)" in result
    assert "• mongo-python-driver (pymongo)" in result


def test_get_test_env_vars_no_config(tmp_path):
    """Test get_test_env_vars with no environment variables configured."""
    config = {
        "repo": {
            "base_dir": str(tmp_path),
            "groups": {
                "pymongo": {
                    "repos": ["git@github.com:mongodb/mongo-python-driver.git"]
                }
            }
        }
    }

    env_vars = get_test_env_vars(config, "pymongo", "mongo-python-driver", tmp_path)
    assert env_vars == {}


def test_get_test_env_vars_with_repo_specific_vars(tmp_path):
    """Test get_test_env_vars with repo-specific environment variables."""
    config = {
        "repo": {
            "base_dir": str(tmp_path),
            "groups": {
                "pymongo": {
                    "repos": ["git@github.com:mongodb/mongo-python-driver.git"],
                    "test_env": {
                        "mongo-python-driver": {
                            "DRIVERS_TOOLS": "{base_dir}/{group}/drivers-evergreen-tools",
                            "TEST_VAR": "test_value"
                        }
                    }
                }
            }
        }
    }

    env_vars = get_test_env_vars(config, "pymongo", "mongo-python-driver", tmp_path)
    assert "DRIVERS_TOOLS" in env_vars
    assert "TEST_VAR" in env_vars
    assert env_vars["TEST_VAR"] == "test_value"
    assert env_vars["DRIVERS_TOOLS"] == f"{tmp_path}/pymongo/drivers-evergreen-tools"


def test_get_test_env_vars_nonexistent_group(tmp_path):
    """Test get_test_env_vars with a group that doesn't exist."""
    config = {
        "repo": {
            "base_dir": str(tmp_path),
            "groups": {
                "pymongo": {
                    "repos": ["git@github.com:mongodb/mongo-python-driver.git"]
                }
            }
        }
    }

    env_vars = get_test_env_vars(config, "nonexistent", "some-repo", tmp_path)
    assert env_vars == {}


def test_expand_env_var_value_with_placeholders(tmp_path):
    """Test _expand_env_var_value with placeholders."""
    value = "{base_dir}/{group}/drivers-evergreen-tools"
    expanded = _expand_env_var_value(value, tmp_path, "pymongo")
    expected = str(Path(tmp_path) / "pymongo" / "drivers-evergreen-tools")
    assert expanded == expected


def test_expand_env_var_value_with_tilde(tmp_path):
    """Test _expand_env_var_value with tilde expansion."""
    value = "~/some/path"
    expanded = _expand_env_var_value(value, tmp_path, "pymongo")
    # Should expand to user's home directory
    assert expanded.startswith(str(Path.home()))
    expected_suffix = str(Path("some") / "path")
    assert expected_suffix in expanded


def test_expand_env_var_value_plain_string(tmp_path):
    """Test _expand_env_var_value with a plain string."""
    value = "plain_value"
    expanded = _expand_env_var_value(value, tmp_path, "pymongo")
    assert expanded == "plain_value"


def test_expand_env_var_value_non_string(tmp_path):
    """Test _expand_env_var_value with non-string value."""
    value = 123
    expanded = _expand_env_var_value(value, tmp_path, "pymongo")
    assert expanded == "123"
