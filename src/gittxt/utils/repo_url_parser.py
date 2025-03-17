from urllib.parse import urlparse
import re


def parse_github_url(url: str) -> dict:
    """
    Parse a GitHub URL to extract owner, repository name, branch, and optional subdirectory.

    Supports:
    - repo URL: https://github.com/user/repo.git
    - branch URL: https://github.com/user/repo/tree/branch
    - subdir URL: https://github.com/user/repo/tree/branch/subdir
    - SSH URL: git@github.com:user/repo.git
    """

    data = {"owner": None, "repo": None, "branch": None, "subdir": None}

    # Handle SSH URL: git@github.com:user/repo.git
    ssh_pattern = re.compile(
        r"git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^.]+)(\.git)?"
    )
    ssh_match = ssh_pattern.match(url)
    if ssh_match:
        data.update(ssh_match.groupdict())
        return data

    # Parse HTTPS URLs
    parsed = urlparse(url)
    if "github.com" not in parsed.netloc:
        raise ValueError("URL is not a valid GitHub link")

    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repo URL format")

    data["owner"] = path_parts[0]
    data["repo"] = path_parts[1].replace(".git", "")

    if len(path_parts) >= 4 and path_parts[2] == "tree":
        data["branch"] = path_parts[3]
        if len(path_parts) > 4:
            data["subdir"] = "/".join(path_parts[4:])
    else:
        data["branch"] = "main"  # Default fallback

    return data


# Example usage:
if __name__ == "__main__":
    test_urls = [
        "https://github.com/sandy-sp/gittxt.git",
        "https://github.com/sandy-sp/gittxt",
        "https://github.com/sandy-sp/gittxt/tree/UI-Dev",
        "https://github.com/sandy-sp/gittxt/tree/ui-dev-2/src/gittxt_ui",
        "git@github.com:sandy-sp/gittxt.git",
    ]
    for url in test_urls:
        print(parse_github_url(url))
