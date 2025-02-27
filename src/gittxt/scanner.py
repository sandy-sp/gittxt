import os
import concurrent.futures
import multiprocessing
import hashlib
import json
from gittxt.logger import get_logger

logger = get_logger(__name__)

# Define cache storage inside `src/gittxt-outputs/cache/`
SRC_DIR = os.path.dirname(__file__)  # `src/gittxt/`
OUTPUT_DIR = os.path.join(SRC_DIR, "../gittxt-outputs")  # `src/gittxt-outputs/`
CACHE_DIR = os.path.join(OUTPUT_DIR, "cache")  # `src/gittxt-outputs/cache/`

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class Scanner:
    def __init__(self, repo_name, root_path, include_patterns=None, exclude_patterns=None, size_limit=None):
        """Initialize the scanner with repository name and settings."""
        self.repo_name = repo_name
        self.root_path = root_path
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.size_limit = size_limit
        self.max_workers = self.calculate_optimal_workers()
        self.cache_reset = False  # Flag to track cache resets

        # Cache file specific to the repository
        self.cache_file = os.path.join(CACHE_DIR, f"{self.repo_name}_cache.json")
        self.cache = self.load_cache()

    def calculate_optimal_workers(self):
        """Dynamically determine the optimal number of workers based on file count and CPU cores."""
        file_count = sum(len(files) for _, _, files in os.walk(self.root_path))
        cpu_count = multiprocessing.cpu_count()

        if file_count < 100:
            return 2
        elif file_count < 500:
            return min(4, cpu_count)
        else:
            return min(8, cpu_count)

    def load_cache(self):
        """Load the existing cache from a file if it exists."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                logger.warning(f"Cache file {self.cache_file} is corrupted. Resetting cache.")
                os.remove(self.cache_file)  # Delete corrupted cache file
                self.cache_reset = True  # Set flag to indicate cache reset
                return {}  # Reset cache
        return {}

    def save_cache(self):
        """Save the updated cache to disk."""
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=4)

    def get_file_hash(self, file_path):
        """Generate a hash for a file based on content."""
        hasher = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Skipping file {file_path} due to error: {e}")
            return None

    def is_excluded(self, file_path):
        """Check if the file should be excluded based on patterns or size."""
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return True
        if self.size_limit and os.path.getsize(file_path) > self.size_limit:
            return True
        return False

    def is_included(self, file_path):
        """Check if the file should be included based on patterns."""
        if not self.include_patterns:
            return True  # Include all if no pattern is specified
        return any(file_path.endswith(pattern) for pattern in self.include_patterns)

    def process_file(self, file_path):
        """Check if a file should be processed and return its path if valid."""
        if self.is_included(file_path) and not self.is_excluded(file_path):
            file_stats = os.stat(file_path)
            file_hash = self.get_file_hash(file_path)

            # Check cache for changes
            cached_entry = self.cache.get(file_path)
            if cached_entry:
                if (
                    cached_entry["size"] == file_stats.st_size
                    and cached_entry["mtime"] == file_stats.st_mtime
                    and cached_entry["hash"] == file_hash
                ):
                    logger.debug(f"Skipping unchanged file: {file_path}")
                    return None  # Skip unchanged file

            # Update cache with new/modified file info
            self.cache[file_path] = {
                "size": file_stats.st_size,
                "mtime": file_stats.st_mtime,
                "hash": file_hash,
            }
            return file_path
        return None

    def scan_directory(self):
        """Scan directory using multi-threading, applying caching."""
        valid_files = []
        self.cache_reset = False  # Reset cache flag
        self.cache = self.load_cache()  # Load cache

        if self.cache_reset:
            logger.info("Cache was reset due to corruption. Forcing a full scan.")
            self.cache = {}  # Ensure cache starts fresh

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for root, _, files in os.walk(self.root_path):
                if ".git" in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(self.process_file, file_path))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_files.append(result)

        self.save_cache()  # Save cache after scanning

        logger.info(f"Scanning complete. {len(valid_files)} new/modified files found using {self.max_workers} workers.")
        return valid_files
