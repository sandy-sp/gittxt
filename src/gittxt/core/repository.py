import git
import tempfile
from pathlib import Path
from gittxt.core.logger import Logger
from gittxt.utils.repo_url_parser import parse_github_url
from gittxt.utils.cleanup_utils import delete_directory

logger = Logger.get_logger(__name__)


class RepositoryHandler:
    """
    Handles local path usage or remote GitHub cloning for scanning.
    Extracts subdir and branch if specified in the URL or in the constructor.
    """

    def __init__(
        self,
        source: str | Path,
        branch: str = None,
        subdir: str = "",
        cache_dir: Path = None,
    ):
        self.source = str(source)
        self.subdir = subdir
        self.branch = branch or "main"
        self.cache_dir = cache_dir or Path(tempfile.mkdtemp(prefix="gittxt_"))

        if isinstance(source, Path) or (
            isinstance(source, str) and Path(source).exists()
        ):
            self.repo_path = Path(source).resolve()
            self.is_remote = False
        elif isinstance(source, str) and (
            "github.com" in source or source.startswith("git@")
        ):
            self.repo_url = source
            self.is_remote = True
        else:
            raise ValueError(f"Unsupported repository source: {source}")

    async def resolve(self) -> Path:
        if self.is_remote:
            return await self._clone_and_resolve()
        return self.repo_path

    async def _clone_and_resolve(self) -> Path:
        parsed = parse_github_url(self.repo_url)
        host = parsed.get("host")
        owner = parsed.get("owner")
        repo_name = parsed.get("repo")
        branch = parsed.get("branch") or self.branch
        subdir = parsed.get("subdir") or self.subdir

        if self.repo_url.startswith("git@"):
            git_url = f"git@{host}:{owner}/{repo_name}.git"
        else:
            git_url = f"https://{host}/{owner}/{repo_name}.git"
        if not git_url.endswith(".git"):
            git_url += ".git"

        temp_dir = self._prepare_temp_dir(repo_name)
        self._clone_remote_repo(git_url, branch, temp_dir)

        self.repo_path = temp_dir
        self.subdir = subdir
        self.branch = branch

        logger.info(
            f"🔄 Remote repo cloned: {repo_name}, subdir={subdir}, branch={branch}"
        )
        return temp_dir

    def _prepare_temp_dir(self, repo_name: str) -> Path:
        temp_dir = self.cache_dir / repo_name
        if temp_dir.exists():
            delete_directory(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    def _clone_remote_repo(self, git_url: str, branch: str, temp_dir: Path):
        try:
            logger.info(
                f"🚀 Cloning repository: {git_url} (branch={branch}) => {temp_dir}"
            )
            git.Repo.clone_from(git_url, str(temp_dir), depth=1, branch=branch)
            self.branch = branch
        except git.GitCommandError as e:
            logger.warning(f"⚠️ Initial clone failed: {e}")
            logger.info("🔁 Retrying without branch specification...")
            try:
                git.Repo.clone_from(git_url, str(temp_dir), depth=1)
                self.branch = "main"  # fallback assumption (could be refined)
            except Exception as fallback_error:
                delete_directory(temp_dir)
                raise RuntimeError(
                    f"❌ Both clone attempts failed.\nGit URL: {git_url}\nBranch attempted: {branch}\n"
                    f"Original error: {e}\nFallback error: {fallback_error}"
                ) from fallback_error

    def get_local_path(self) -> tuple[str, str, bool, str, str]:
        """
        Return (repo_path, subdir, is_remote, repo_name, used_branch)
        """
        if self.is_remote:
            return (
                str(self.repo_path),
                self.subdir,
                True,
                self.repo_path.name,
                self.branch,
            )
        else:
            path = Path(self.source).resolve()
            if not path.exists() or not path.is_dir():
                raise FileNotFoundError(
                    f"❌ Local path not found or not a directory: {path}. "
                    f"Ensure the input is a valid local Git repository root."
                )
            return (str(path), self.subdir, False, path.name, self.branch)
