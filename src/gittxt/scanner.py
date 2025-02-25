import os
from gittxt.logger import get_logger

logger = get_logger(__name__)

class Scanner:
    def __init__(self, root_path, include_patterns=None, exclude_patterns=None, size_limit=None):
        self.root_path = root_path
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.size_limit = size_limit

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

    def scan_directory(self):
        """Scan directory and return a list of valid file paths."""
        valid_files = []
        for root, _, files in os.walk(self.root_path):
            if ".git" in root:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                if self.is_included(file_path) and not self.is_excluded(file_path):
                    valid_files.append(file_path)

        logger.info(f"Scanning complete. {len(valid_files)} files found.")
        return valid_files
