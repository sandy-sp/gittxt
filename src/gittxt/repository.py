import os
import tempfile
import git
from gittxt.logger import get_logger

logger = get_logger(__name__)

class RepositoryHandler:
    def __init__(self, source, branch=None):
        self.source = source
        self.branch = branch
        self.local_path = None

    def is_remote_repo(self):
        return self.source.startswith("http") or self.source.endswith(".git")

    def clone_repository(self):
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Cloning repository into: {temp_dir}")

        clone_args = {"depth": 1} if not self.branch else {"branch": self.branch, "depth": 1}

        try:
            git.Repo.clone_from(self.source, temp_dir, **clone_args)
            self.local_path = temp_dir
            return temp_dir
        except git.exc.GitCommandError as e:
            logger.error(f"Error cloning repository: {e}")
            return None

    def get_local_path(self):
        if self.is_remote_repo():
            return self.clone_repository()
        return self.source
