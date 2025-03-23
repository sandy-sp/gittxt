from urllib.parse import urlparse
import re
from pathlib import Path

def build_github_url(repo_url: str, rel_path: Path) -> str:
    if not repo_url:
        return ""

    repo_url = repo_url.replace("git@github.com:", "https://github.com/")
    repo_url = repo_url.replace(".git", "")
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 2:
        return ""

    owner, repo = path_parts[:2]
    subdir = "/".join(path_parts[3:]) if "tree" in path_parts else ""
    branch = "main"

    tree_match = re.search(r"/tree/([^/]+)", parsed.path)
    if tree_match:
        branch = tree_match.group(1)

    base_url = f"https://github.com/{owner}/{repo}/blob/{branch}"
    if subdir:
        return f"{base_url}/{subdir}/{rel_path.as_posix()}"
    return f"{base_url}/{rel_path.as_posix()}"


def build_github_repo_url(repo_url: str) -> str:
    """
    Used for repo-level URL in README (no /blob/)
    """
    if not repo_url:
        return ""

    repo_url = repo_url.replace("git@github.com:", "https://github.com/")
    repo_url = repo_url.replace(".git", "")
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 2:
        return ""

    owner, repo = path_parts[:2]
    subdir = "/".join(path_parts[3:]) if "tree" in path_parts else ""
    branch = "main"

    tree_match = re.search(r"/tree/([^/]+)", parsed.path)
    if tree_match:
        branch = tree_match.group(1)

    base_url = f"https://github.com/{owner}/{repo}/tree/{branch}"
    if subdir:
        return f"{base_url}/{subdir}"
    return base_url