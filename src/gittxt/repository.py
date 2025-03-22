from pathlib import Path
import git
from gittxt.logger import Logger
from gittxt.utils.repo_url_parser import parse_github_url
from gittxt.config import ConfigManager

config = ConfigManager.load_config()
logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """Handles GitHub repo cloning and local directory resolution."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()
    TEMP_DIR = BASE_OUTPUT_DIR / "temp"

    def __init__(self, source: str, branch: str = None):
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

    def _clone_remote_repo(self, git_url: str, branch: str, temp_dir: Path) -> bool:
        try:
            logger.info(f"🚀 Cloning repository into: {temp_dir}")
            clone_args = {"depth": 1}
            if branch:
                clone_args["branch"] = branch
            git.Repo.clone_from(git_url, str(temp_dir), **clone_args)
            logger.info(f"✅ Clone successful: {temp_dir}")
            return True
        except git.GitCommandError as e:
            logger.warning(f"⚠️ Git clone failed for {git_url} on branch {branch}: {e}")
            # Retry without specifying branch if fallback needed
            try:
                logger.info(f"🔄 Retrying clone without branch (use repo default)")
                git.Repo.clone_from(git_url, str(temp_dir), depth=1)
                return True
            except Exception as err:
                logger.error(f"❌ Retry clone failed: {err}")
                return False

    def get_local_path(self) -> tuple[str, str, bool, str]:
        """
        Return repo folder path + subdirectory (if provided).

        Returns:
            (repo_path, subdir, is_remote, repo_name)
        """
        if self.is_remote_repo(self.source):
            parsed = parse_github_url(self.source)
            repo_url_scheme = "git@" if self.source.startswith("git@") else "https://github.com/"
            git_url = f"{repo_url_scheme}{parsed['owner']}/{parsed['repo']}.git"
            branch = self.branch_override or parsed.get("branch")

            subdir = parsed.get("subdir") or ""
            repo_name = parsed["repo"].replace(".git", "")
            temp_dir = self._prepare_temp_dir(repo_name)
            success = self._clone_remote_repo(git_url, branch, temp_dir)
            if not success:
                return None, None, self.is_remote, repo_name
            return str(temp_dir), subdir, self.is_remote, repo_name

        else:
            path = Path(self.source).resolve()
            repo_name = path.name
            if not path.exists():
                logger.error(f"❌ Invalid local repo path: {self.source}")
                return None, None, self.is_remote, repo_name

            if not path.is_dir():
                logger.error(f"❌ Provided path is not a directory: {self.source}")
                return None, None, self.is_remote, repo_name

            if not (path / ".git").exists():
                logger.warning(f"⚠️ No .git directory found in: {self.source} (treated as non-Git repo)")

            logger.info(f"✅ Using local repository: {path}")
            return str(path), "", self.is_remote, repo_name
