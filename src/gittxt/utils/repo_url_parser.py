from urllib.parse import urlparse
import re
import os


def parse_github_url(url: str) -> dict:
    """
    Parse GitHub.com URLs: https://github.com/user/repo(.git)/tree/branch/subdir
    or SSH: git@github.com:user/repo.git
    """
    data = {"host": None, "owner": None, "repo": None, "branch": None, "subdir": None}

    allowed_domains = ["github.com"]
    allowed_domains.extend(os.getenv("GITTXT_ALLOWED_DOMAINS", "").split(","))

    # SSH form
    ssh_pattern = re.compile(
        r"git@(?P<host>[^:]+):(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"
    )
    ssh_match = ssh_pattern.match(url)
    if ssh_match:
        data.update(ssh_match.groupdict())
        if data["host"] not in allowed_domains:
            raise ValueError(f"Unsupported Git host: {data['host']}")
        return data

    # HTTPS form
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL: Missing hostname")

    data["host"] = parsed.netloc
    if data["host"] not in allowed_domains:
        raise ValueError(f"Unsupported Git host: {data['host']}")

    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub URL format: Missing owner/repo")

    data["owner"] = path_parts[0]
    data["repo"] = path_parts[1].replace(".git", "")

    # optional branch/subdir
    if len(path_parts) >= 4 and path_parts[2] == "tree":
        data["branch"] = path_parts[3]
        if len(path_parts) > 4:
            data["subdir"] = "/".join(path_parts[4:])
    else:
        data["branch"] = "main"

    return data
