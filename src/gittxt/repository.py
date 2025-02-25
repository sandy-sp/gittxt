import os
import tempfile
import git

class RepositoryHandler:
    def __init__(self, source, branch=None):
        self.source = source
        self.branch = branch
        self.local_path = None

    def is_remote_repo(self):
        """Check if the source is a remote Git repository."""
        return self.source.startswith("http") or self.source.endswith(".git")

    def clone_repository(self):
        """Clone the repository to a temporary directory."""
        temp_dir = tempfile.mkdtemp()
        print(f"Cloning repository into: {temp_dir}")

        clone_args = {"depth": 1} if not self.branch else {"branch": self.branch, "depth": 1}

        try:
            git.Repo.clone_from(self.source, temp_dir, **clone_args)
            self.local_path = temp_dir
            return temp_dir
        except git.exc.GitCommandError as e:
            print(f"Error cloning repository: {e}")
            return None

    def get_local_path(self):
        """Return the path to the local repository."""
        if self.is_remote_repo():
            return self.clone_repository()
        return self.source  # Local path is used directly
