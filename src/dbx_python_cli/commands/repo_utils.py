"""Shared utilities for repository operations."""


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
                if repo_dir.is_dir() and (repo_dir / ".git").exists():
                    repos.append(
                        {
                            "name": repo_dir.name,
                            "path": repo_dir,
                            "group": group_dir.name,
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


def list_repos(base_dir, format_style="default"):
    """
    List all repositories in a formatted way.

    Args:
        base_dir: Path to the base directory containing group subdirectories
        format_style: Output format style ('default', 'tree', 'grouped', or 'simple')

    Returns:
        str: Formatted list of repositories
    """
    repos = find_all_repos(base_dir)

    if not repos:
        return None

    if format_style == "tree":
        # Tree format with group as parent
        from collections import defaultdict

        grouped = defaultdict(list)
        for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
            grouped[repo["group"]].append(repo["name"])

        lines = []
        sorted_groups = sorted(grouped.keys())
        for i, group in enumerate(sorted_groups):
            is_last_group = i == len(sorted_groups) - 1
            group_prefix = "└──" if is_last_group else "├──"
            lines.append(f"{group_prefix} {group}/")

            repo_names = grouped[group]
            for j, repo_name in enumerate(repo_names):
                is_last_repo = j == len(repo_names) - 1
                continuation = "    " if is_last_group else "│   "
                repo_prefix = "└──" if is_last_repo else "├──"
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

        grouped = defaultdict(list)
        for repo in sorted(repos, key=lambda r: (r["group"], r["name"])):
            grouped[repo["group"]].append(repo["name"])

        lines = []
        sorted_groups = sorted(grouped.keys())
        for i, group in enumerate(sorted_groups):
            is_last_group = i == len(sorted_groups) - 1
            group_prefix = "└──" if is_last_group else "├──"
            lines.append(f"{group_prefix} {group}/")

            repo_names = grouped[group]
            for j, repo_name in enumerate(repo_names):
                is_last_repo = j == len(repo_names) - 1
                continuation = "    " if is_last_group else "│   "
                repo_prefix = "└──" if is_last_repo else "├──"
                lines.append(f"{continuation}{repo_prefix} {repo_name}")
        return "\n".join(lines)
