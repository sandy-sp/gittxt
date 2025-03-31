from urllib.parse import urlparse
import re
import os


def parse_github_url(url: str) -> dict:
    """
    Parse GitHub.com URLs:
      - HTTPS: https://github.com/user/repo(.git)/tree/branch/subdir
      - SSH: git@github.com:user/repo(.git)

    Returns a dict with:
      - host, owner, repo, branch, subdir
    """
    data = {"host": None, "owner": None, "repo": None, "branch": None, "subdir": None}

    # Load allowed domains (with fallback)
    allowed_domains = ["github.com"]
    allowed_domains += [d.strip() for d in os.getenv("GITTXT_ALLOWED_DOMAINS", "").split(",") if d.strip()]

    # === SSH format ===
    ssh_pattern = re.compile(
        r"git@(?P<host>[^:]+):(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"
    )
    ssh_match = ssh_pattern.match(url)
    if ssh_match:
        data.update(ssh_match.groupdict())
        if data["host"] not in allowed_domains:
            raise ValueError(f"Unsupported Git host: {data['host']}")
        data["repo"] = data["repo"].replace(".git", "")
        data["branch"] = "main"
        return data

    # === HTTPS format ===
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: '{url}' is missing hostname")

    data["host"] = parsed.netloc
    if data["host"] not in allowed_domains:
        raise ValueError(f"Unsupported Git host: {data['host']}")

    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub URL: '{url}' does not include owner and repo")

    data["owner"] = path_parts[0]
    data["repo"] = path_parts[1].replace(".git", "")

    # Detect optional branch and subdir: /tree/branch/...
    if len(path_parts) >= 4 and path_parts[2] == "tree":
        data["branch"] = path_parts[3]
        if len(path_parts) > 4:
            subdir = "/".join(path_parts[4:]).strip("/")
            data["subdir"] = subdir if subdir else None
    else:
        data["branch"] = "main"

    return data
