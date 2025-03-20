from urllib.parse import urlparse
import re

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

    # 1️⃣ Handle SSH-style URLs (e.g., git@github.com:user/repo.git)
    ssh_pattern = re.compile(
        r"git@(?P<host>[^:]+):(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"
    )
    ssh_match = ssh_pattern.match(url)
    if ssh_match:
        data.update(ssh_match.groupdict())
        return data

    # 2️⃣ Handle HTTPS URLs (e.g., https://github.com/user/repo or custom GHE)
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL: Missing hostname")

    data["host"] = parsed.netloc

    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub/GHE URL format: Missing owner/repo")

    data["owner"] = path_parts[0]
    data["repo"] = path_parts[1].replace(".git", "")

    # Handle optional branch and subdir
    if len(path_parts) >= 4 and path_parts[2] == "tree":
        data["branch"] = path_parts[3]
        if len(path_parts) > 4:
            data["subdir"] = "/".join(path_parts[4:])
    else:
        data["branch"] = "main"  # default fallback branch for ambiguous URLs

    return data


# --- Quick CLI test block ---
if __name__ == "__main__":
    test_urls = [
        "https://github.com/sandy-sp/gittxt.git",
        "https://github.com/sandy-sp/gittxt/tree/dev/docs",
        "git@github.com:sandy-sp/gittxt.git",
        "https://git.mycompany.com/ml-team/private-repo.git",
        "git@git.mycompany.com:ml-team/private-repo.git"
    ]

    for url in test_urls:
        print(f"\n🔗 URL: {url}")
        print(parse_github_url(url))
