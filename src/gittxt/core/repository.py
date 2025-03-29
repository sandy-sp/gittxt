import git
from pathlib import Path
from gittxt.core.logger import Logger
from gittxt.utils.repo_url_parser import parse_github_url
from gittxt.core.config import ConfigManager
from gittxt.utils.cleanup_utils import delete_directory

logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """
    Handles local path usage or remote GitHub cloning for scanning.
    Extracts subdir and branch if specified in the URL or in the constructor.
    """

    def __init__(self, source: str, branch: str = None):
        self.source = source
        self.branch_override = branch
        self.is_remote = self._is_remote_repo(source)
        self.config = ConfigManager.load_config()

    def _is_remote_repo(self, source: str) -> bool:
        return "github.com" in source or source.startswith("git@")

    def _prepare_temp_dir(self, repo_name: str) -> Path:
        base_output_dir = Path(self.config.get("output_dir"))
        temp_dir = base_output_dir / "temp" / repo_name
        if temp_dir.exists():
            delete_directory(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    def _clone_remote_repo(self, git_url: str, branch: str, temp_dir: Path):
        try:
            logger.info(f"🚀 Cloning repository: {git_url} (branch={branch}) => {temp_dir}")
            clone_args = {"depth": 1}
            if branch:
                clone_args["branch"] = branch
            git.Repo.clone_from(git_url, str(temp_dir), **clone_args)
        except git.GitCommandError as e:
            logger.warning(f"⚠️ Initial clone failed for '{git_url}' with branch='{branch}': {e}")
            logger.info("🔁 Retrying without branch specification...")
            try:
                git.Repo.clone_from(git_url, str(temp_dir), depth=1)
            except Exception as fallback_error:
                raise RuntimeError(
                    f"❌ Both clone attempts failed.\n"
                    f"Git URL: {git_url}\n"
                    f"Branch attempted: {branch}\n"
                    f"Original error: {e}\n"
                    f"Fallback error: {fallback_error}"
                ) from fallback_error

    def get_local_path(self) -> tuple[str, str, bool, str, str]:
        """
        Return (repo_path, subdir, is_remote, repo_name, used_branch).
        This helps the scanner or output builder to include subdir/branch info in final output.
        """
        if self.is_remote:
            parsed = parse_github_url(self.source)
            host = parsed.get("host")
            owner = parsed.get("owner")
            repo_name = parsed.get("repo")
            subdir = parsed.get("subdir") or ""
            branch = self.branch_override or parsed.get("branch", "main")

            # Construct a final Git URL. Might be SSH or HTTPS.
            if self.source.startswith("git@"):
                git_url = f"git@{host}:{owner}/{repo_name}.git"
            else:
                git_url = f"https://{host}/{owner}/{repo_name}.git"

            temp_dir = self._prepare_temp_dir(repo_name)
            self._clone_remote_repo(git_url, branch, temp_dir)
            repo_path = str(temp_dir)
            logger.info(f"🔄 Remote repo cloned: {repo_name}, subdir={subdir}, branch={branch}")

            return (repo_path, subdir, True, repo_name, branch)
        else:
            # Local path
            path = Path(self.source).resolve()
            if not path.exists() or not path.is_dir():
                raise FileNotFoundError(
                    f"❌ Local path not found or not a directory: {path}. "
                    f"Ensure the input is a valid local Git repository root."
                )
            repo_name = path.name
            logger.info(f"✅ Using local repository: {path}")
            return (str(path), "", False, repo_name, None)
