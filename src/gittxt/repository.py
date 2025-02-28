import os
import tempfile
import git
from urllib.parse import urlparse
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """Handles remote and local Git repository management for Gittxt."""

    def __init__(self, source, branch=None, reuse_existing=True):
        """
        Initialize repository handler.

        :param source: Local path or remote Git URL.
        :param branch: Git branch to clone (if applicable).
        :param reuse_existing: Reuse already cloned repositories to prevent redundancy.
        """
        self.source = source
        self.branch = branch
        self.reuse_existing = reuse_existing
        self.local_path = None

    def is_remote_repo(self):
        """Check if the source is a remote Git repository."""
        return self.source.startswith("http") or self.source.endswith(".git") or "git@" in self.source

    def get_repo_name(self):
        """Extract repository name from the URL."""
        parsed_url = urlparse(self.source)
        repo_name = os.path.basename(parsed_url.path).replace(".git", "").strip()
        return repo_name if repo_name else "unknown_repo"

    def clone_repository(self):
        """Clone the repository into a named temp directory instead of a random one."""
        repo_name = self.get_repo_name()
        temp_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gittxt-outputs", "temp")
        temp_dir = os.path.join(temp_base, repo_name)

        # Ensure the directory structure exists
        os.makedirs(temp_base, exist_ok=True)

        # Avoid redundant cloning if reuse_existing is enabled
        if self.reuse_existing and os.path.exists(temp_dir):
            logger.info(f"✅ Repository already cloned: {temp_dir}")
            self.local_path = temp_dir
            return temp_dir

        logger.info(f"🚀 Cloning repository into: {temp_dir}")

        # Clone with shallow depth for efficiency
        clone_args = {"depth": 1} if not self.branch else {"branch": self.branch, "depth": 1}

        try:
            git.Repo.clone_from(self.source, temp_dir, **clone_args)
            self.local_path = temp_dir
            return temp_dir
        except git.exc.GitCommandError as e:
            logger.error(f"❌ Error cloning repository: {e}")
            return None

    def get_local_path(self):
        """
        Get the local path of the repository.

        If it's a remote repo, clone it first. If it's local, return the provided path.
        """
        if self.is_remote_repo():
            return self.clone_repository()
        if os.path.exists(self.source):
            return self.source
        logger.error(f"❌ Invalid repository path: {self.source}")
        return None
