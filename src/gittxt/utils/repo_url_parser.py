from urllib.parse import urlparse
import re

def parse_github_url(url: str) -> dict:
    """
    Parse GitHub/GHE URLs:
    Supports:
    - https://github.com/user/repo.git
    - https://github.com/user/repo/tree/branch/subdir
    - git@github.com:user/repo.git
    - git@github.mycompany.com:user/repo.git
    """
    data = {"owner": None, "repo": None, "branch": None, "subdir": None}

    # SSH-style (including GHE)
    ssh_pattern = re.compile(
        r"git@(?P<host>[^:]+):(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"
    )
    ssh_match = ssh_pattern.match(url)
    if ssh_match:
        data.update(ssh_match.groupdict())
        return data

    # HTTPS URLs (GitHub.com or GHE)
    parsed = urlparse(url)
    if "github" not in parsed.netloc:
        raise ValueError("URL is not a valid GitHub/GHE link")

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
        data["branch"] = "main"  # Default fallback for ambiguous URLs

    return data
