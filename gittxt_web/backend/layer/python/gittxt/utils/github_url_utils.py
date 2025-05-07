from urllib.parse import urlparse
import re
from pathlib import Path


def build_github_url(
    repo_url: str, rel_path: Path, branch: str = "main", subdir: str = None
) -> str:
    """
    Build a direct GitHub file URL in the format:
    https://github.com/user/repo/blob/branch/path/to/file
    """
    if not repo_url or not rel_path:
        return ""

    # Normalize SSH → HTTPS
    repo_url = repo_url.replace("git@github.com:", "https://github.com/")
    repo_url = repo_url.replace(".git", "")
    repo_url = repo_url.rstrip("/")

    # Remove tree/blob segments
    repo_url = re.sub(r"/(tree|blob)/[^/]+.*$", "", repo_url)

    rel = rel_path.as_posix()
    if subdir:
        # Prevent double subdir (e.g. subdir/subdir/file)
        try:
            rel = Path(rel_path).relative_to(subdir).as_posix()
        except ValueError:
            rel = rel_path.as_posix()
        subdir_path = f"{subdir.strip('/')}/"
    else:
        subdir_path = ""

    return f"{repo_url}/blob/{branch}/{subdir_path}{rel}"


def build_github_repo_url(repo_url: str) -> str:
    """
    Builds the repo-level URL (no /blob/) to use in ZIP summaries, etc.
    """
    if not repo_url:
        return ""

    repo_url = repo_url.replace("git@github.com:", "https://github.com/")
    repo_url = repo_url.replace(".git", "").rstrip("/")

    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 2:
        return ""

    owner, repo = path_parts[:2]
    branch = "main"
    subdir = ""

    tree_match = re.search(r"/tree/([^/]+)", parsed.path)
    if tree_match:
        branch = tree_match.group(1)
        remaining = parsed.path.split(f"/tree/{branch}/")
        if len(remaining) > 1:
            subdir = remaining[1].strip("/")

    base_url = f"https://github.com/{owner}/{repo}/tree/{branch}"
    if subdir:
        return f"{base_url}/{subdir}"
    return base_url
