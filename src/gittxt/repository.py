import os
import git
import json
import functools
from urllib.parse import urlparse
from gittxt.logger import Logger
from typing import Optional, Dict, Any
from datetime import datetime
from gittxt.config import ConfigManager  # Import config to load cache settings

logger = Logger.get_logger(__name__)

class RepositoryHandler:
    """Handles remote and local Git repository management for Gittxt."""

    # Define absolute path for repository storage
    BASE_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs"))
    TEMP_DIR = os.path.join(BASE_OUTPUT_DIR, "temp")

    # Load max cache size dynamically from config
    config = ConfigManager.load_config()
    MAX_CACHE_SIZE = config.get("max_cache_size", 10)  # Default to 10 if not set

    # Use an LRU (Least Recently Used) cache strategy for repository reuse
    _clone_cache = functools.lru_cache(maxsize=MAX_CACHE_SIZE)(dict)

    def __init__(self, source: str, branch: Optional[str] = None, reuse_existing: bool = True):
        """
        Initialize repository handler.

        Args:
            source (str): Local path or remote Git URL.
            branch (Optional[str]): Git branch to clone (if applicable).
            reuse_existing (bool): Reuse already cloned repositories to prevent redundancy. Defaults to True.

        Raises:
            ValueError: If the source is neither a valid local path nor a remote URL.
        """
        if not self.is_remote_repo(source) and not os.path.exists(source):
            raise ValueError(f"Invalid source: {source}. Must be a valid local path or remote Git URL.")

        # Use absolute paths for local sources
        self.source = source if self.is_remote_repo(source) else os.path.abspath(source)
        self.branch = branch
        self.reuse_existing = reuse_existing
        self.local_path = None

    def is_remote_repo(self, source: str) -> bool:
        """
        Check if the source is likely a remote Git repository.

        Args:
            source (str): The source to check.

        Returns:
            bool: True if the source appears to be a remote repository, False otherwise.
        """
        parsed_url = urlparse(source)
        return bool(parsed_url.scheme in ("http", "https", "git") or 
                    parsed_url.netloc and parsed_url.path or 
                    source.startswith("git@") or 
                    source.endswith(".git"))

    @staticmethod
    def parse_github_url(url: str) -> Optional[Dict[str, str]]:
        """
        Parse a GitHub URL and return the owner and repository name.
        
        Args:
            url (str): A GitHub repository URL.

        Returns:
            Optional[Dict[str, str]]: Dictionary containing 'owner' and 'repo' keys, or None if parsing fails.
        """
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        # Handle SSH URLs like git@github.com:owner/repo.git
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        if url.startswith('git@'):
            _, owner_repo = url.split(':')
            owner, repo = owner_repo.split('/')
            return {'owner': owner, 'repo': repo.rstrip('.git')}

        elif len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].rstrip('.git')
            return {'owner': owner, 'repo': repo}

        logger.error(f"Failed to parse GitHub URL: {url}")
        return None

    def get_repo_name(self) -> Optional[str]:
        """
        Extract repository name from the URL or local path.
        
        Returns:
            Optional[str]: Repository name on success, None on failure.
        """
        if os.path.exists(self.source):
            return os.path.basename(os.path.normpath(self.source))

        parsed = self.parse_github_url(self.source)
        if parsed:
            return parsed['repo']

        logger.error(f"Failed to parse repository name from: {self.source}")
        return None

    def clone_repository(self) -> Optional[str]:
        """
        Clone the repository into a named temp directory inside `gittxt-outputs/temp/`.

        Returns:
            Optional[str]: Local path on success, or None on failure.
        """
        repo_name = self.get_repo_name()
        if not repo_name:
            return None

        cache_key = (self.source, self.branch)
        if self.reuse_existing and cache_key in self._clone_cache:
            logger.info(f"Repository already cloned (cache): {self._clone_cache[cache_key]['path']}")
            self.local_path = self._clone_cache[cache_key]['path']
            return self.local_path

        temp_dir = os.path.join(self.TEMP_DIR, repo_name)
        os.makedirs(self.TEMP_DIR, exist_ok=True)

        # Check if the directory already exists and reuse it
        if self.reuse_existing and os.path.exists(temp_dir):
            logger.info(f"Repository already cloned: {temp_dir}")
            self.local_path = temp_dir
            self._clone_cache[cache_key] = {
                'path': temp_dir,
                'timestamp': datetime.now().isoformat()
            }
            return temp_dir

        logger.info(f"Cloning repository into: {temp_dir}")

        clone_args = {"depth": 1}
        if self.branch:
            clone_args["branch"] = self.branch

        try:
            git.Repo.clone_from(self.source, temp_dir, **clone_args)
            self.local_path = temp_dir
            self._clone_cache[cache_key] = {
                'path': temp_dir,
                'timestamp': datetime.now().isoformat()
            }

            self._prune_clone_cache()
            logger.info(f"Clone successful: {temp_dir}")
            return temp_dir

        except git.exc.GitCommandError as e:
            logger.error(f"Git error while cloning repository: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during cloning: {e}")

        return None

    def _prune_clone_cache(self) -> None:
        """
        Prune the cache to maintain the max cache size limit dynamically.
        """
        while len(self._clone_cache) > self.MAX_CACHE_SIZE:
            oldest_entry = min(self._clone_cache.items(), key=lambda item: item[1]['timestamp'])
            del self._clone_cache[oldest_entry[0]]
            logger.info(f"Pruned cache entry: {oldest_entry[0]}")

    def get_local_path(self) -> Optional[str]:
        """
        Get the local path of the repository.
        
        If it's remote, clone it to the temp directory.
        If it's local, verify the directory exists.
        
        Returns:
            Optional[str]: Local path on success, None on failure.
        """
        if self.is_remote_repo(self.source):
            return self.clone_repository()
            
        if os.path.exists(self.source):
            logger.info(f"Using local repository: {self.source}")
            return self.source
            
        logger.error(f"Invalid repository path: {self.source}")
        return None

    @classmethod
    def clear_clone_cache(cls) -> None:
        """
        Clear all entries in the clone cache.
        """
        cls._clone_cache.clear()
        logger.info("Cleared clone cache.")