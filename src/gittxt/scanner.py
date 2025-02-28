import os
import mimetypes
import sqlite3
import concurrent.futures
import hashlib
import subprocess
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class Scanner:
    """Handles scanning of local directories and filtering based on file type and patterns."""

    CACHE_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gittxt-outputs", "cache", "scan_cache.db")

    def __init__(self, root_path, include_patterns=None, exclude_patterns=None, size_limit=None):
        """
        Initialize scanner with filtering options.

        :param root_path: Path to the local directory or cloned repository.
        :param include_patterns: List of file extensions to include (default: all).
        :param exclude_patterns: List of file extensions or folders to exclude.
        :param size_limit: Maximum file size in bytes to process.
        """
        self.root_path = root_path
        self.include_patterns = self._parse_patterns(include_patterns)
        self.exclude_patterns = self._parse_patterns(exclude_patterns)
        self.size_limit = size_limit
        self._initialize_cache()

    def _initialize_cache(self):
        """Ensure SQLite cache database is set up for incremental scanning."""
        os.makedirs(os.path.dirname(self.CACHE_DB), exist_ok=True)
        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS file_cache (
                path TEXT PRIMARY KEY,
                hash TEXT
            )"""
        )
        conn.commit()
        conn.close()

    def _parse_patterns(self, patterns):
        """Convert comma-separated string patterns into a list."""
        if isinstance(patterns, str):
            return [p.strip() for p in patterns.split(",")]
        return patterns if patterns else []

    def is_text_file(self, file_path):
        """Determine if a file is text-based using MIME type detection."""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type and mime_type.startswith("text")

    def generate_tree_summary(self):
        """Generate a folder structure summary using 'tree' command."""
        try:
            return subprocess.check_output(["tree", self.root_path, "-L", "2"], text=True)
        except FileNotFoundError:
            return "⚠️ Tree command not available."

    def get_file_hash(self, file_path):
        """Generate SHA256 hash of the file content for caching."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"❌ Error hashing file {file_path}: {e}")
            return None

    def scan_directory(self):
        """Scan directory using multi-threading, filtering, and caching."""
        valid_files = []
        non_text_files = []
        tree_summary = self.generate_tree_summary()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.process_file, os.path.join(root, file)): file
                for root, _, files in os.walk(self.root_path) for file in files
            }

            for future in concurrent.futures.as_completed(futures):
                file_path, is_text = future.result()
                if is_text:
                    valid_files.append(file_path)
                else:
                    non_text_files.append(file_path)

        logger.info(f"✅ Scanning complete. {len(valid_files)} text files found.")
        logger.info(f"⚠️ {len(non_text_files)} non-text files skipped.")
        return valid_files, tree_summary

    def process_file(self, file_path):
        """Process a file and determine if it should be included or skipped."""
        if not self.is_text_file(file_path):
            return file_path, False  # Non-text file

        if any(pattern in file_path for pattern in self.exclude_patterns):
            return None, False  # Excluded file

        if self.include_patterns and not any(file_path.endswith(p) for p in self.include_patterns):
            return None, False  # Not in included patterns

        if self.size_limit and os.path.getsize(file_path) > self.size_limit:
            return None, False  # Exceeds size limit

        # Check cache
        file_hash = self.get_file_hash(file_path)
        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM file_cache WHERE path = ?", (file_path,))
        cached_entry = cursor.fetchone()

        if cached_entry and cached_entry[0] == file_hash:
            logger.info(f"⚡ Skipping unchanged file: {file_path}")
            conn.close()
            return None, False  # Unchanged file

        # Update cache
        cursor.execute("REPLACE INTO file_cache (path, hash) VALUES (?, ?)", (file_path, file_hash))
        conn.commit()
        conn.close()

        return file_path, True  # Valid text file
