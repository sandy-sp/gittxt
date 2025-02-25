import os
import concurrent.futures
import multiprocessing
from gittxt.logger import get_logger

logger = get_logger(__name__)

class Scanner:
    def __init__(self, root_path, include_patterns=None, exclude_patterns=None, size_limit=None):
        self.root_path = root_path
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.size_limit = size_limit
        self.max_workers = self.calculate_optimal_workers()

    def calculate_optimal_workers(self):
        """Dynamically determine the optimal number of workers based on file count and CPU cores."""
        file_count = sum(len(files) for _, _, files in os.walk(self.root_path))
        cpu_count = multiprocessing.cpu_count()

        # Adjust worker count based on file size:
        if file_count < 100:
            return 3  # Small project
        elif file_count < 500:
            return min(6, cpu_count)  # Medium project
        else:
            return min(9, cpu_count)  # Large project

    def is_excluded(self, file_path):
        """Check if the file should be excluded based on patterns or size."""
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                logger.debug(f"Excluding {file_path} (matched pattern '{pattern}')")
                return True
        if self.size_limit and os.path.getsize(file_path) > self.size_limit:
            logger.debug(f"Excluding {file_path} (size limit exceeded)")
            return True
        return False

    def is_included(self, file_path):
        """Check if the file should be included based on patterns."""
        if not self.include_patterns:
            return True  # If no include patterns, include all files
        return any(file_path.endswith(pattern) for pattern in self.include_patterns)

    def process_file(self, file_path):
        """Check if a file should be included and return its path if valid."""
        if self.is_included(file_path) and not self.is_excluded(file_path):
            return file_path
        return None

    def scan_directory(self):
        """Scan directory using multi-threading and return a list of valid file paths."""
        valid_files = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for root, _, files in os.walk(self.root_path):
                if ".git" in root:
                    continue  # Skip .git directory
                for file in files:
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(self.process_file, file_path))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_files.append(result)

        logger.info(f"Scanning complete. {len(valid_files)} files found using {self.max_workers} workers.")
        return valid_files
