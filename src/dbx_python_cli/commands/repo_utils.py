"""Shared utilities for repository operations."""


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
        from collections import defaultdict

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
        from collections import defaultdict

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
        from collections import defaultdict

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
