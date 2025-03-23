from urllib.parse import urlparse
import re
import os

def parse_github_url(url: str) -> dict:
    """
    Parse GitHub.com and GitHub Enterprise (GHE) URLs:
    Supports:
    - https://github.com/user/repo.git
    - https://github.com/user/repo/tree/branch/subdir
    - git@github.com:user/repo.git
    - https://git.mycompany.com/user/repo
    - git@mycompany.com:user/repo.git
    """
    data = {"host": None, "owner": None, "repo": None, "branch": None, "subdir": None}

    # Allow github.com and *.mycompany.com (you can expand this list later)
    allowed_domains = ["github.com"]
    allowed_domains.extend(os.getenv("GITTXT_ALLOWED_DOMAINS", "").split(","))  # env-configurable

    # SSH-style URLs
    ssh_pattern = re.compile(
        r"git@(?P<host>[^:]+):(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"
    )
    ssh_match = ssh_pattern.match(url)
    if ssh_match:
        data.update(ssh_match.groupdict())
        if data["host"] not in allowed_domains:
            raise ValueError(f"Unsupported Git host: {data['host']}")
        return data

    # HTTPS URLs
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL: Missing hostname")

    data["host"] = parsed.netloc

    if data["host"] not in allowed_domains:
        raise ValueError(f"Unsupported Git host: {data['host']}")

    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub/GHE URL format: Missing owner/repo")

    data["owner"] = path_parts[0]
    data["repo"] = path_parts[1].replace(".git", "")

    # Optional branch/subdir
    if len(path_parts) >= 4 and path_parts[2] == "tree":
        data["branch"] = path_parts[3]
        if len(path_parts) > 4:
            data["subdir"] = "/".join(path_parts[4:])
    else:
        data["branch"] = "main"

    return data


# CLI Test Block
if __name__ == "__main__":
    test_urls = [
        "https://github.com/sandy-sp/gittxt.git",
        "https://github.com/sandy-sp/gittxt/tree/dev/docs",
        "git@github.com:sandy-sp/gittxt.git",
        "https://git.mycompany.com/ml-team/private-repo.git",
        "git@git.mycompany.com:ml-team/private-repo.git",
        "https://gitlab.com/user/repo",  # This should now raise ValueError
    ]

    for url in test_urls:
        try:
            print(f"\n🔗 URL: {url}")
            print(parse_github_url(url))
        except ValueError as e:
            print(f"❌ {e}")
