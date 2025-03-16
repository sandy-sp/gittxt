from pathlib import Path
import git
from urllib.parse import urlparse
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """Handles remote and local Git repository management for Gittxt."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()
    TEMP_DIR = BASE_OUTPUT_DIR / "temp"

    _clone_cache = {}

    def __init__(self, source, branch=None, reuse_existing=True):
        """
        Initialize repository handler.

        :param source: Local path or remote Git URL.
        :param branch: Git branch to clone (if applicable).
        :param reuse_existing: Reuse already cloned repositories to prevent redundancy.
        """
        if self.is_remote_repo(source):
            self.source = source
        else:
            self.source = Path(source).resolve()
        self.branch = branch
        self.reuse_existing = reuse_existing
        self.local_path = None

    def is_remote_repo(self, source: str) -> bool:
        parsed_url = urlparse(source)
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
        if isinstance(self.source, Path) and self.source.exists():
            return self.source.name
        if isinstance(self.source, str):
            parsed_url = urlparse(self.source)
            repo_name = Path(parsed_url.path).stem
            if not repo_name:
                logger.error(f"❌ Could not extract repository name from: {self.source}")
                return None
            return repo_name
        return None

    def clone_repository(self) -> str or None:
        repo_name = self.get_repo_name()
        if not repo_name:
            return None

        cache_key = (self.source, self.branch)
        if self.reuse_existing and cache_key in RepositoryHandler._clone_cache:
            logger.info(f"✅ Repository already cloned (cache): {RepositoryHandler._clone_cache[cache_key]}")
            self.local_path = RepositoryHandler._clone_cache[cache_key]
            return str(self.local_path)

        temp_dir = self.TEMP_DIR / repo_name
        temp_dir.mkdir(parents=True, exist_ok=True)

        if self.reuse_existing and temp_dir.exists():
            logger.info(f"✅ Repository already cloned: {temp_dir}")
            self.local_path = temp_dir
            RepositoryHandler._clone_cache[cache_key] = temp_dir
            return str(temp_dir)

        logger.info(f"🚀 Cloning repository into: {temp_dir}")

        clone_args = {"depth": 1}
        if self.branch:
            clone_args["branch"] = self.branch

        try:
            git.Repo.clone_from(self.source, str(temp_dir), **clone_args)
            self.local_path = temp_dir
            RepositoryHandler._clone_cache[cache_key] = temp_dir
            logger.info(f"✅ Clone successful: {temp_dir}")
            return str(temp_dir)
        except git.exc.GitCommandError as e:
            logger.error(f"❌ Git error while cloning repository: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during cloning: {e}")

        return None

    def get_local_path(self) -> str or None:
        if self.is_remote_repo(self.source):
            return self.clone_repository()
        if isinstance(self.source, Path) and self.source.exists():
            logger.info(f"✅ Using local repository: {self.source}")
            return str(self.source)
        logger.error(f"❌ Invalid repository path: {self.source}")
        return None
