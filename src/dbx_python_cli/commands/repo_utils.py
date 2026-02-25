"""Repository utilities and helper functions."""

import tomllib
from pathlib import Path
from collections import defaultdict

import typer


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

    For repos with packages in subdirectories, returns a list of subdirectories to install.
    For regular repos, returns None (install from root).

    Args:
        config: Configuration dictionary
        group_name: Name of the group (e.g., 'langchain')
        repo_name: Name of the repository (e.g., 'langchain-mongodb')

    Returns:
        list: List of install directories, or None if packages are at the root
    """
    groups = get_repo_groups(config)
    if group_name not in groups:
        return None

    install_dirs_config = groups[group_name].get("install_dirs", {})
    return install_dirs_config.get(repo_name)


def get_build_commands(config, group_name, repo_name):
    """
    Get build commands for a repository.

    For repos that need a build step before installation (e.g., cmake builds),
    returns a list of shell commands to run.

    Args:
        config: Configuration dictionary
        group_name: Name of the group (e.g., 'django')
        repo_name: Name of the repository (e.g., 'libmongocrypt')

    Returns:
        list: List of build commands, or None if no build needed
    """
    groups = get_repo_groups(config)
    if group_name not in groups:
        return None

    build_commands_config = groups[group_name].get("build_commands", {})
    return build_commands_config.get(repo_name)


def get_test_runner(config, group_name, repo_name):
    """
    Get test runner configuration for a repository.

    Returns the test runner command/script if configured, otherwise None (use pytest).

    Args:
        config: Configuration dictionary
        group_name: Name of the group (e.g., 'django')
        repo_name: Name of the repository (e.g., 'django')

    Returns:
        str: Test runner path/command, or None for default pytest
    """
    groups = get_repo_groups(config)
    if group_name not in groups:
        return None

    test_runner_config = groups[group_name].get("test_runner", {})
    return test_runner_config.get(repo_name)


def get_test_env_vars(config, group_name, repo_name, base_dir):
    """
    Get environment variables for test runs.

    Returns a dictionary of environment variables to set when running tests.
    Supports both group-level and repo-specific environment variables.

    Args:
        config: Configuration dictionary
        group_name: Name of the group (e.g., 'pymongo')
        repo_name: Name of the repository (e.g., 'mongo-python-driver')
        base_dir: Base directory path for resolving relative paths

    Returns:
        dict: Dictionary of environment variable names to values
    """
    groups = get_repo_groups(config)
    if group_name not in groups:
        return {}

    env_vars = {}

    # Get group-level environment variables
    group_env_config = groups[group_name].get("test_env", {})
    if isinstance(group_env_config, dict):
        # Check if there are common env vars for the group
        for key, value in group_env_config.items():
            if not isinstance(value, dict):
                # This is a group-level env var
                env_vars[key] = _expand_env_var_value(value, base_dir, group_name)

    # Get repo-specific environment variables (these override group-level)
    repo_env_config = groups[group_name].get("test_env", {}).get(repo_name, {})
    if isinstance(repo_env_config, dict):
        for key, value in repo_env_config.items():
            env_vars[key] = _expand_env_var_value(value, base_dir, group_name)

    return env_vars


def _expand_env_var_value(value, base_dir, group_name):
    """
    Expand special placeholders in environment variable values.

    Supports:
    - {base_dir}: Expands to the base directory path
    - {group}: Expands to the group name
    - ~: Expands to user home directory

    Args:
        value: The environment variable value (string)
        base_dir: Base directory path
        group_name: Name of the group

    Returns:
        str: Expanded value
    """
    if not isinstance(value, str):
        return str(value)

    # Expand placeholders
    expanded = value.replace("{base_dir}", str(base_dir))
    expanded = expanded.replace("{group}", group_name)

    # Expand user home directory
    expanded = str(Path(expanded).expanduser())

    return expanded


def extract_repo_name_from_url(url):
    """
    Extract repository name from a git URL.

    Args:
        url: Git URL (e.g., "git@github.com:mongodb/mongo-python-driver.git")

    Returns:
        str: Repository name (e.g., "mongo-python-driver")
    """
    # Handle both SSH and HTTPS URLs
    # SSH: git@github.com:mongodb/mongo-python-driver.git
    # HTTPS: https://github.com/mongodb/mongo-python-driver.git
    if url.endswith(".git"):
        url = url[:-4]
    return url.split("/")[-1]


def find_all_repos(base_dir):
    """
    Find all cloned repositories in the base directory.

    Args:
        base_dir: Path to the base directory containing group subdirectories

    Returns:
        list: List of dictionaries with 'name', 'path', and 'group' keys
    """
    repos = []
    if not base_dir.exists():
        return repos

    # Look for repos in group subdirectories
    for group_dir in base_dir.iterdir():
        if group_dir.is_dir():
            for repo_dir in group_dir.iterdir():
                if repo_dir.is_dir():
                    # Check if it's a git repo
                    if (repo_dir / ".git").exists():
                        repos.append(
                            {
                                "name": repo_dir.name,
                                "path": repo_dir,
                                "group": group_dir.name,
                            }
                        )
                    # Also check if it's a project (has pyproject.toml but no .git)
                    # This allows projects to be found by install command
                    elif (
                        group_dir.name == "projects"
                        and (repo_dir / "pyproject.toml").exists()
                    ):
                        repos.append(
                            {
                                "name": repo_dir.name,
                                "path": repo_dir,
                                "group": "projects",
                            }
                        )
    return repos


def find_repo_by_name(repo_name, base_dir):
    """
    Find a repository by name in the base directory.

    Args:
        repo_name: Name of the repository to find
        base_dir: Path to the base directory containing group subdirectories

    Returns:
        dict: Dictionary with 'name', 'path', and 'group' keys, or None if not found
    """
    all_repos = find_all_repos(base_dir)
    for repo in all_repos:
        if repo["name"] == repo_name:
            return repo
    return None


def list_repos(base_dir, format_style="default", config=None):
    """
    List all repositories in a formatted way.

    Args:
        base_dir: Path to the base directory containing group subdirectories
        format_style: Output format style ('default', 'tree', 'grouped', or 'simple')
        config: Optional config dict to compare available vs cloned repos

    Returns:
        str: Formatted list of repositories
    """
    repos = find_all_repos(base_dir)

    # If config is provided, get available repos from config
    available_repos = {}
    if config:
        groups = config.get("repo", {}).get("groups", {})
        for group_name, group_config in groups.items():
            repo_urls = group_config.get("repos", [])
            for url in repo_urls:
                repo_name = extract_repo_name_from_url(url)
                if group_name not in available_repos:
                    available_repos[group_name] = []
                available_repos[group_name].append(repo_name)

    # If no repos cloned and no config, return None
    if not repos and not available_repos:
        return None

    if format_style == "tree":
        # Tree format with group as parent
        # Build cloned repos dict
        cloned = defaultdict(list)
        for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
            cloned[repo["group"]].append(repo["name"])

        # Merge available and cloned groups
        all_groups = set(cloned.keys()) | set(available_repos.keys())

        lines = []
        sorted_groups = sorted(all_groups)
        for i, group in enumerate(sorted_groups):
            is_last_group = i == len(sorted_groups) - 1
            group_prefix = "└──" if is_last_group else "├──"
            lines.append(f"{group_prefix} {group}/")

            # Get all repos for this group (available and cloned)
            available_in_group = set(available_repos.get(group, []))
            cloned_in_group = set(cloned.get(group, []))
            all_repos_in_group = sorted(available_in_group | cloned_in_group)

            for j, repo_name in enumerate(all_repos_in_group):
                is_last_repo = j == len(all_repos_in_group) - 1
                continuation = "    " if is_last_group else "│   "
                repo_prefix = "└──" if is_last_repo else "├──"

                # Add status indicator if config is provided
                if config:
                    is_cloned = repo_name in cloned_in_group
                    is_available = repo_name in available_in_group
                    if is_cloned and is_available:
                        status = "✓"  # Cloned
                    elif is_cloned and not is_available:
                        status = "?"  # Cloned but not in config
                    else:
                        status = "○"  # Available but not cloned
                    lines.append(f"{continuation}{repo_prefix} {status} {repo_name}")
                else:
                    lines.append(f"{continuation}{repo_prefix} {repo_name}")
        return "\n".join(lines)

    elif format_style == "grouped":
        # Group repos by group name
        grouped = defaultdict(list)
        for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
            grouped[repo["group"]].append(repo["name"])

        lines = []
        for group in sorted(grouped.keys()):
            lines.append(f"  [{group}]")
            for repo_name in grouped[group]:
                lines.append(f"    • {repo_name}")
        return "\n".join(lines)

    elif format_style == "simple":
        # Simple list with group in parentheses
        lines = []
        for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
            lines.append(f"  • {repo['name']} ({repo['group']})")
        return "\n".join(lines)

    else:  # default - use tree format
        # Default format: tree structure
        # Build cloned repos dict
        cloned = defaultdict(list)
        for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
            cloned[repo["group"]].append(repo["name"])

        # Merge available and cloned groups
        all_groups = set(cloned.keys()) | set(available_repos.keys())

        lines = []
        sorted_groups = sorted(all_groups)
        for i, group in enumerate(sorted_groups):
            is_last_group = i == len(sorted_groups) - 1
            group_prefix = "└──" if is_last_group else "├──"
            group_label = typer.style(f"{group}/", fg=typer.colors.CYAN, bold=True)
            lines.append(f"{group_prefix} {group_label}")

            # Get all repos for this group (available and cloned)
            available_in_group = set(available_repos.get(group, []))
            cloned_in_group = set(cloned.get(group, []))
            all_repos_in_group = sorted(available_in_group | cloned_in_group)

            for j, repo_name in enumerate(all_repos_in_group):
                is_last_repo = j == len(all_repos_in_group) - 1
                continuation = "    " if is_last_group else "│   "
                repo_prefix = "└──" if is_last_repo else "├──"

                # Add status indicator if config is provided
                if config:
                    is_cloned = repo_name in cloned_in_group
                    is_available = repo_name in available_in_group
                    if is_cloned and is_available:
                        status = typer.style("✓", fg=typer.colors.GREEN)
                    elif is_cloned and not is_available:
                        status = typer.style("?", fg=typer.colors.MAGENTA)
                    else:
                        status = typer.style("○", fg=typer.colors.YELLOW)
                    lines.append(f"{continuation}{repo_prefix} {status} {repo_name}")
                else:
                    lines.append(f"{continuation}{repo_prefix} {repo_name}")
        return "\n".join(lines)
