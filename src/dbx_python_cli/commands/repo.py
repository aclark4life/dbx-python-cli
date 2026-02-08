"""Repository management helper functions."""

import tomllib
from pathlib import Path


def get_config_path():
    """Get the path to the user config file."""
    config_dir = Path.home() / ".config" / "dbx-python-cli"
    return config_dir / "config.toml"


def get_default_config_path():
    """Get the path to the default config file shipped with the package."""
    return Path(__file__).parent.parent / "config.toml"


def get_config():
    """Load configuration from user config or default config."""
    user_config_path = get_config_path()
    default_config_path = get_default_config_path()

    # Try user config first
    if user_config_path.exists():
        with open(user_config_path, "rb") as f:
            return tomllib.load(f)

    # Fall back to default config
    if default_config_path.exists():
        with open(default_config_path, "rb") as f:
            return tomllib.load(f)

    # If neither exists, return empty config
    return {}


def get_base_dir(config):
    """Get the base directory for cloning repos."""
    base_dir = config.get("repo", {}).get("base_dir", "~/repos")
    return Path(base_dir).expanduser()


def get_repo_groups(config):
    """Get repository groups from config."""
    return config.get("repo", {}).get("groups", {})


def get_install_dirs(config, group_name, repo_name):
    """
    Get install directories for a repository.

    For monorepos, returns a list of subdirectories to install.
    For regular repos, returns None (install from root).

    Args:
        config: Configuration dictionary
        group_name: Name of the group (e.g., 'langchain')
        repo_name: Name of the repository (e.g., 'langchain-mongodb')

    Returns:
        list: List of install directories, or None if not a monorepo
    """
    groups = get_repo_groups(config)
    if group_name not in groups:
        return None

    install_dirs_config = groups[group_name].get("install_dirs", {})
    return install_dirs_config.get(repo_name)
