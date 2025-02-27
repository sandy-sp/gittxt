import os
import git
from urllib.parse import urlparse
from gittxt.logger import get_logger

logger = get_logger(__name__)

# Define the directory for storing temporary cloned repositories **inside src/**
SRC_DIR = os.path.dirname(__file__)  # `src/gittxt/`
OUTPUT_DIR = os.path.join(SRC_DIR, "../gittxt-outputs")  # `src/gittxt-outputs/`
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")  # `src/gittxt-outputs/temp/`

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)

class RepositoryHandler:
    def __init__(self, source, branch=None):
        self.source = source
        self.branch = branch
        self.local_path = None

    def is_remote_repo(self):
        """Check if the given source is a remote Git repository."""
        return self.source.startswith("http") or self.source.endswith(".git") or self.source.startswith("git@")

    def get_repo_name(self):
        """Extract repository name from the URL."""
        parsed_url = urlparse(self.source)
        repo_name = os.path.basename(parsed_url.path).replace(".git", "").strip()
        return repo_name if repo_name else "unknown_repo"

    def clone_repository(self):
        """Clone the repository into `src/gittxt-outputs/temp/` and avoid redundant cloning."""
        repo_name = self.get_repo_name()
        repo_path = os.path.join(TEMP_DIR, repo_name)

        # Check if the repo already exists
        if os.path.exists(repo_path):
            logger.info(f"Repository {repo_name} already exists. Using cached clone.")
            self.local_path = repo_path
            return repo_path

        logger.info(f"Cloning repository into: {repo_path}")

        clone_args = {"depth": 1} if not self.branch else {"branch": self.branch, "depth": 1}

        try:
            git.Repo.clone_from(self.source, repo_path, **clone_args)
            self.local_path = repo_path
            return repo_path
        except git.exc.GitCommandError as e:
            logger.error(f"Error cloning repository: {e}")
            return None

    def get_local_path(self):
        """Return the path to the local repository, cloning if necessary."""
        if self.is_remote_repo():
            return self.clone_repository()
        return self.source  # Use directly if it's a local directory
