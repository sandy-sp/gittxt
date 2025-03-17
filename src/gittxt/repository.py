from pathlib import Path
import git
from gittxt.logger import Logger
from gittxt.utils.repo_url_parser import parse_github_url

logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """Handles GitHub repo cloning and local directory resolution."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()
    TEMP_DIR = BASE_OUTPUT_DIR / "temp"

    def __init__(self, source: str, branch: str = None):
        """
        Initialize repository handler.

        :param source: Local path or remote GitHub URL.
        :param branch: Override branch (optional).
        """
        self.source = source
        self.branch_override = branch
        self.repo_meta = {}
        self.is_remote = self.is_remote_repo(self.source)

    def is_remote_repo(self, source: str) -> bool:
        return "github.com" in source or source.startswith("git@")

    def _prepare_temp_dir(self, repo_name: str) -> Path:
        temp_dir = self.TEMP_DIR / repo_name
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    def _clone_remote_repo(self, git_url: str, branch: str, temp_dir: Path):
        logger.info(f"🚀 Cloning repository into: {temp_dir}")
        clone_args = {"depth": 1}
        if branch:
            clone_args["branch"] = branch
        git.Repo.clone_from(git_url, str(temp_dir), **clone_args)
        logger.info(f"✅ Clone successful: {temp_dir}")

    def get_local_path(self) -> tuple[str, str]:
        """
        Return repo folder path + subdirectory (if provided).

        Returns:
            (repo_path, subdir)
        """
        if self.is_remote_repo(self.source):
            parsed = parse_github_url(self.source)
            git_url = f"https://github.com/{parsed['owner']}/{parsed['repo']}.git"
            branch = self.branch_override or parsed.get("branch", "main")
            subdir = parsed.get("subdir") or ""

            repo_name = parsed["repo"]
            temp_dir = self._prepare_temp_dir(repo_name)
            self._clone_remote_repo(git_url, branch, temp_dir)
            return str(temp_dir), subdir, self.is_remote
        else:
            path = Path(self.source).resolve()
            if not path.exists():
                logger.error(f"❌ Invalid local repo path: {self.source}")
                return None, ""

            # Accept non-git folders for local testing
            if not path.is_dir():
                logger.error(f"❌ Provided path is not a directory: {self.source}")
                return None, ""

            # OPTIONAL: only apply strict .git check if you want to force "real repos"
            if not (path / ".git").exists():
                logger.warning(f"⚠️ No .git directory found in: {self.source} (treated as non-Git repo)")

            logger.info(f"✅ Using local repository: {path}")
            return str(path), "", self.is_remote
