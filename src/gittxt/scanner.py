import os

class Scanner:
    def __init__(self, root_path, exclude_patterns=None, size_limit=None):
        self.root_path = root_path
        self.exclude_patterns = exclude_patterns or []
        self.size_limit = size_limit  # In bytes

    def is_excluded(self, file_path):
        """Check if the file should be excluded based on patterns or size."""
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return True
        if self.size_limit and os.path.getsize(file_path) > self.size_limit:
            return True
        return False

    def scan_directory(self):
        """Scan directory and return a list of valid file paths."""
        valid_files = []
        for root, _, files in os.walk(self.root_path):
            if ".git" in root:  # Skip .git directory
                continue

            for file in files:
                file_path = os.path.join(root, file)
                if not self.is_excluded(file_path):
                    valid_files.append(file_path)

        return valid_files
