from pathlib import Path
import git
from gittxt.core.logger import Logger
from gittxt.utils.repo_url_parser import parse_github_url
from gittxt import config
from gittxt.utils.cleanup_utils import delete_directory 

logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """Handles GitHub repo cloning and local directory resolution."""

    def __init__(self, source: str, branch: str = None):
        self.source = source
        self.branch_override = branch
        self.is_remote = self.is_remote_repo(self.source)

    def is_remote_repo(self, source: str) -> bool:
        return "github.com" in source or source.startswith("git@")

    def _prepare_temp_dir(self, repo_name: str) -> Path:
        base_output_dir = Path(config.get("output_dir")).resolve()
        temp_root = base_output_dir / "temp"
        temp_dir = temp_root / repo_name

        if temp_dir.exists():
            delete_directory(temp_dir)

        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    def _clone_remote_repo(self, git_url: str, branch: str, temp_dir: Path):
        try:
            logger.info(f"🚀 Cloning repository {git_url} (branch: {branch}) into: {temp_dir}")
            clone_args = {"depth": 1}
            if branch:
                clone_args["branch"] = branch
            git.Repo.clone_from(git_url, str(temp_dir), **clone_args)
        except git.GitCommandError as e:
            logger.warning(f"⚠️ Clone with branch '{branch}' failed for {git_url}: {e}. Retrying without branch parameter.")
            try:
                git.Repo.clone_from(git_url, str(temp_dir), depth=1)
            except Exception as err:
                raise RuntimeError(f"❌ Retry clone without branch failed: {err}")

    def get_local_path(self) -> tuple[str, str, bool, str]:
        """
        Return repo folder path + subdirectory (if provided).

        Returns:
            (repo_path, subdir, is_remote, repo_name)
        """
        logger.info(f"🔗 Resolving repository at {self.source}")
        if self.is_remote_repo(self.source):
            parsed = parse_github_url(self.source)
            repo_url_scheme = "git@" if self.source.startswith("git@") else "https://github.com/"
            git_url = f"{repo_url_scheme}{parsed['owner']}/{parsed['repo']}.git"
            branch = self.branch_override or parsed.get("branch")

            subdir = parsed.get("subdir") or ""
            if ".." in subdir:
                raise ValueError(f"❌ Unsafe subdirectory path detected: {subdir}")

            repo_name = parsed["repo"].replace(".git", "")
            temp_dir = self._prepare_temp_dir(repo_name)
            try:
                self._clone_remote_repo(git_url, branch, temp_dir)
            except Exception as e:
                raise RuntimeError(f"❌ Failed to clone repository: {e}")
            logger.info(f"🔄 Subdirectory inside repo: {subdir or 'root'}")
            return str(temp_dir), subdir, self.is_remote, repo_name

        else:
            path = Path(self.source).resolve()
            repo_name = path.name
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Invalid local repo path: {self.source}")
            return str(path), "", self.is_remote, repo_name
