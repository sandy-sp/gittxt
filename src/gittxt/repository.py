import os
import re
import git
from urllib.parse import urlparse
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

def parse_github_url(url: str):
    """
    Parse a GitHub URL into components: owner, repo, branch, and optional sub_path.
    Returns a dict with keys:
      {
        'owner': str,
        'repo': str,
        'branch': str or None,
        'sub_path': str or None
      }
    or None if the URL doesn't look like a valid GitHub URL.

    Example GitHub URLs handled:
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      - https://github.com/owner/repo/tree/branch/some/sub/folder
      - https://github.com/owner/repo/blob/branch/some/file.txt
    """
    parsed = urlparse(url)
    # Must be on github.com or subdomain
    if not parsed.netloc.endswith("github.com"):
        return None

    # Strip leading/trailing slashes and split by "/"
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        return None

    owner = path_parts[0]
    # Remove .git suffix if present
    repo = path_parts[1].replace(".git", "")

    branch = None
    sub_path = None

    # Possible patterns:
    # /owner/repo/tree/<branch>/some/path
    # /owner/repo/blob/<branch>/some/path
    # If path_parts[2] is "tree" or "blob", next item is <branch>.
    if len(path_parts) >= 3 and path_parts[2] in ("tree", "blob"):
        if len(path_parts) >= 4:
            branch = path_parts[3]
        # If more parts exist after the branch name, that's a sub-path
        if len(path_parts) > 4:
            sub_path = "/".join(path_parts[4:])

    return {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "sub_path": sub_path
    }


class RepositoryHandler:
    """
    Handles remote and local Git repository management for Gittxt.
    Automatically detects branch/sub-path from GitHub URLs so the user
    does not need to manually pass --branch if it's included in the URL.
    """

    # Define absolute path for repository storage
    BASE_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs"))
    TEMP_DIR = os.path.join(BASE_OUTPUT_DIR, "temp")
    
    # Class-level cache to reuse already cloned repositories.
    # Key: (source, branch), Value: local clone path.
    _clone_cache = {}

    def __init__(self, source, branch=None, reuse_existing=True):
        """
        :param source: Local path or remote Git URL (e.g. GitHub).
        :param branch: Git branch to clone (optional, if user explicitly provides).
        :param reuse_existing: Reuse already cloned repositories to prevent redundancy.
        """
        # If it's a local path, convert to absolute path. If remote, store verbatim.
        self.source = source if self.is_remote_repo(source) else os.path.abspath(source)
        self.branch = branch
        self.reuse_existing = reuse_existing
        self.local_path = None
        self.sub_path = None

        # If this looks like a GitHub URL, try to parse out branch/subfolder automatically.
        if "github.com" in self.source.lower():
            gh_info = parse_github_url(self.source)
            if gh_info:
                # If no explicit branch was passed, use the one from the URL
                if not self.branch and gh_info['branch']:
                    self.branch = gh_info['branch']
                # Store the sub-path if any (subfolder or single file)
                self.sub_path = gh_info['sub_path']

    def is_remote_repo(self, source: str) -> bool:
        """
        Check if the source is likely a remote Git repository.
        Uses urlparse to see if there's a scheme/netloc, or if it starts with 'git@' or ends with '.git'.
        """
        parsed_url = urlparse(source)
        # If there's a scheme (http, https, git), or a netloc, or .git suffix => likely remote
        if parsed_url.scheme in ("http", "https", "git"):
            return True
        if parsed_url.netloc and parsed_url.path:
            return True
        if source.startswith("git@"):
            return True
        if source.endswith(".git"):
            return True
        return False

    def get_repo_name(self) -> str or None:
        """
        Extract repository name from the URL or local path.
        If it's a local path, just return the leaf folder name.
        If remote, parse from the URL path.
        """
        if os.path.exists(self.source):
            return os.path.basename(os.path.normpath(self.source))

        parsed_url = urlparse(self.source)
        repo_name = os.path.basename(parsed_url.path).replace(".git", "").strip()
        if not repo_name:
            logger.error(f"❌ Could not extract repository name from: {self.source}")
            return None
        return repo_name

    def clone_repository(self) -> str or None:
        """
        Clone the repository into a named temp directory inside `gittxt-outputs/temp/`.
        Returns the local path on success, or None on failure.
        Uses a class-level cache if reuse_existing is True.

        If self.branch is set (auto-detected or user-provided),
        it will attempt to clone that branch. Otherwise defaults to 'main'.
        """
        repo_name = self.get_repo_name()
        if not repo_name:
            return None

        # Decide which branch to use if none was explicitly set
        clone_branch = self.branch if self.branch else "main"

        cache_key = (self.source, clone_branch)
        if self.reuse_existing and cache_key in RepositoryHandler._clone_cache:
            logger.info(f"✅ Repository already cloned (cache): {RepositoryHandler._clone_cache[cache_key]}")
            self.local_path = RepositoryHandler._clone_cache[cache_key]
            return self.local_path

        temp_dir = os.path.join(self.TEMP_DIR, repo_name)
        os.makedirs(self.TEMP_DIR, exist_ok=True)

        # If reuse_existing is enabled and the directory already exists, reuse it.
        if self.reuse_existing and os.path.exists(temp_dir):
            logger.info(f"✅ Repository already cloned: {temp_dir}")
            self.local_path = temp_dir
            RepositoryHandler._clone_cache[cache_key] = temp_dir
            return temp_dir

        logger.info(f"🚀 Cloning repository '{repo_name}' (branch='{clone_branch}') into: {temp_dir}")

        clone_args = {"depth": 1, "branch": clone_branch}

        try:
            git.Repo.clone_from(self.source, temp_dir, **clone_args)
            self.local_path = temp_dir
            RepositoryHandler._clone_cache[cache_key] = temp_dir
            logger.info(f"✅ Clone successful: {temp_dir}")
            return temp_dir
        except git.exc.GitCommandError as e:
            logger.error(f"❌ Git error while cloning repository: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during cloning: {e}")

        return None

    def get_local_path(self) -> str or None:
        """
        Get the local path of the repository.
        If it's a remote URL, clone it first (if not already cloned).
        If it's a local path, verify the directory exists.
        Returns None on failure.
        """
        if self.is_remote_repo(self.source):
            return self.clone_repository()

        # If local path is valid, just return that
        if os.path.exists(self.source):
            logger.info(f"✅ Using local repository: {self.source}")
            return self.source

        logger.error(f"❌ Invalid repository path: {self.source}")
        return None
