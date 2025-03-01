import os
import git
from urllib.parse import urlparse
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """Handles remote and local Git repository management for Gittxt."""

    # Define absolute path for repository storage
    BASE_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs"))
    TEMP_DIR = os.path.join(BASE_OUTPUT_DIR, "temp")

    def __init__(self, source, branch=None, reuse_existing=True):
        """
        Initialize repository handler.

        :param source: Local path or remote Git URL.
        :param branch: Git branch to clone (if applicable).
        :param reuse_existing: Reuse already cloned repositories to prevent redundancy.
        """
        # If it's remote, store source verbatim; if local, convert to absolute path:
        self.source = source if self.is_remote_repo(source) else os.path.abspath(source)
        self.branch = branch
        self.reuse_existing = reuse_existing
        self.local_path = None

    def is_remote_repo(self, source: str) -> bool:
        """
        Check if the source is likely a remote Git repository.
        We do a more robust check using urlparse to see if there's
        a scheme/netloc or if it starts with 'git@' or ends with '.git'.
        """
        parsed_url = urlparse(source)

        # If it has a scheme like http(s) or git, or netloc is present
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
        """Extract repository name from the URL or local path."""
        # If the source is local, just get basename of that directory
        if os.path.exists(self.source):
            return os.path.basename(os.path.normpath(self.source))

        # Otherwise parse the URL
        parsed_url = urlparse(self.source)
        repo_name = os.path.basename(parsed_url.path).replace(".git", "").strip()

        if not repo_name:
            logger.error(f"❌ Could not extract repository name from: {self.source}")
            return None

        return repo_name

    def clone_repository(self) -> str or None:
        """
        Clone the repository into a named temp directory inside `gittxt-outputs/temp/`.
        Returns the path to the cloned repo on success, or None on failure.
        """
        repo_name = self.get_repo_name()
        if not repo_name:
            return None

        temp_dir = os.path.join(self.TEMP_DIR, repo_name)

        # Ensure the directory structure exists
        os.makedirs(self.TEMP_DIR, exist_ok=True)

        # Avoid redundant cloning if reuse_existing is enabled
        if self.reuse_existing and os.path.exists(temp_dir):
            logger.info(f"✅ Repository already cloned: {temp_dir}")
            self.local_path = temp_dir
            return temp_dir

        logger.info(f"🚀 Cloning repository into: {temp_dir}")

        # Construct clone arguments (shallow clone by default)
        clone_args = {"depth": 1}
        if self.branch:
            clone_args["branch"] = self.branch

        try:
            git.Repo.clone_from(self.source, temp_dir, **clone_args)
            self.local_path = temp_dir
            logger.info(f"✅ Clone successful: {temp_dir}")
            return temp_dir

        except git.exc.GitCommandError as e:
            # Example: Branch not found, or invalid credentials, etc.
            error_msg = str(e).lower()
            logger.error(f"❌ Git error while cloning repository: {e}")

            # OPTIONAL: Attempt fallback to main/master if branch not found:
            # if "remote ref does not exist" in error_msg or "not found" in error_msg:
            #     logger.warning("⚠️ Specified branch not found. Attempting 'main' fallback...")
            #     try:
            #         clone_args["branch"] = "main"
            #         git.Repo.clone_from(self.source, temp_dir, **clone_args)
            #         self.local_path = temp_dir
            #         logger.info(f"✅ Fallback clone successful (branch=main): {temp_dir}")
            #         return temp_dir
            #     except Exception as fallback_err:
            #         logger.error(f"❌ Fallback to 'main' also failed: {fallback_err}")

        except Exception as e:
            logger.error(f"❌ Unexpected error during cloning: {e}")

        return None  # Always return None if cloning fails

    def get_local_path(self) -> str or None:
        """
        Get the local path of the repository. If it's a remote,
        clone it to the temp directory. If it's local, verify
        the directory exists. Returns None on failure.
        """
        # If remote, attempt to clone
        if self.is_remote_repo(self.source):
            return self.clone_repository()

        # If local, confirm it exists
        if os.path.exists(self.source):
            logger.info(f"✅ Using local repository: {self.source}")
            return self.source

        logger.error(f"❌ Invalid repository path: {self.source}")
        return None
