import os
import mimetypes
import sqlite3
import concurrent.futures
import hashlib
import subprocess
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class Scanner:
    """
    Handles scanning of local directories and filtering based on file type and patterns.
    Now supports optional 'docs_only' and 'auto_filter' toggles for advanced filtering.
    """

    BASE_CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs/cache"))
    CACHE_DB = os.path.join(BASE_CACHE_DIR, "scan_cache.db")

    def __init__(
        self,
        root_path,
        include_patterns=None,
        exclude_patterns=None,
        size_limit=None,
        docs_only=False,
        auto_filter=False
    ):
        """
        Initialize the Scanner with filtering options.

        :param root_path: Path to the local directory or cloned repository.
        :param include_patterns: List of file extensions to include (default: all).
        :param exclude_patterns: List of file extensions or folders to exclude.
        :param size_limit: Maximum file size in bytes to process.
        :param docs_only: If True, only documentation files (README, .md, .rst, etc.) are processed.
        :param auto_filter: If True, automatically skip common unwanted/binary file types.
        """
        self.root_path = os.path.abspath(root_path)
        self.include_patterns = self._parse_patterns(include_patterns)
        self.exclude_patterns = self._parse_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.docs_only = docs_only
        self.auto_filter = auto_filter

        self._initialize_cache()

    def _initialize_cache(self):
        """Ensure SQLite cache database is set up for incremental scanning."""
        os.makedirs(self.BASE_CACHE_DIR, exist_ok=True)
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
        logger.debug("✅ Cache database initialized")

    def clear_cache(self):
        """Clear the cache database. Used for testing and ensuring fresh scans."""
        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM file_cache")
        conn.commit()
        conn.close()
        logger.info("🗑️ Cache cleared.")

    def _parse_patterns(self, patterns):
        """Convert comma-separated string patterns into a list of stripped patterns."""
        if isinstance(patterns, str):
            return [p.strip() for p in patterns.split(",")]
        return patterns if patterns else []

    def _is_documentation_file(self, file_path):
        """
        Determine if the file is considered 'documentation'.
        For simplicity, we'll treat these files/folders as docs:
          - Filenames: README*, LICENSE, CONTRIBUTING, CHANGELOG, etc.
          - Any .md, .rst, .txt extension
          - Anything in a '/docs/' folder
        """
        basename = os.path.basename(file_path).lower()
        dirname = os.path.dirname(file_path).lower()
        _, ext = os.path.splitext(basename)

        doc_filenames = {
            "readme", "license", "contributing", "changelog"
        }
        doc_extensions = {".md", ".rst", ".txt"}

        # Check if name starts with any of doc_filenames (e.g. README.md or LICENSE.txt)
        if any(basename.startswith(fn) for fn in doc_filenames):
            return True
        # Check extension
        if ext in doc_extensions:
            return True
        # If 'docs' is in the folder path
        if "docs" in dirname:
            return True

        return False

    def _auto_filter_file(self, file_path):
        """
        Skip common unwanted or binary file types automatically.
        E.g., .log, .gz, .tar, .jpg, .csv (optionally), etc.
        This is separate from 'is_text_file' or explicit includes/excludes,
        giving us an extra layer of default filtering if auto_filter is enabled.
        """
        # Define some typical patterns we want to skip automatically
        # (beyond what's done by is_text_file).
        # For instance, log files, archive files, big data file types...
        auto_exclude_ext = {
            ".log", ".gz", ".tar", ".jpg", ".jpeg", ".png", ".csv", ".pdf", ".doc", ".docx"
        }
        basename = os.path.basename(file_path).lower()
        _, ext = os.path.splitext(basename)

        # If the extension is in auto_exclude_ext, skip it
        if ext in auto_exclude_ext:
            logger.debug(f"❌ Auto-filter skipping file: {file_path}")
            return True

        return False

    def is_text_file(self, file_path):
        """
        Determine if a file is text-based using MIME type detection.
        We also maintain an explicit set of known binary extensions.
        """
        binary_extensions = {
            ".mp4", ".avi", ".mov", ".tar.gz", ".zip", ".exe", ".bin", ".jpeg", ".png", ".gif", ".pdf"
        }

        # Check file extension first
        if any(file_path.endswith(ext) for ext in binary_extensions):
            logger.debug(f"❌ Skipping binary file based on extension: {file_path}")
            return False

        # Fallback to MIME type detection
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            return False

        if mime_type.startswith("text"):
            return True

        logger.debug(f"❌ Skipping non-text file (MIME: {mime_type}): {file_path}")
        return False

    def generate_tree_summary(self):
        """Generate a folder structure summary using 'tree' command (if available)."""
        try:
            return subprocess.check_output(["tree", self.root_path, "-L", "2"], text=True)
        except FileNotFoundError:
            logger.warning("⚠️ Tree command not found, skipping repository structure summary.")
            return "⚠️ Tree command not available."
        except subprocess.SubprocessError as e:
            logger.error(f"❌ Error generating tree summary: {e}")
            return "⚠️ Error generating repository structure."

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
        """
        Scan directory using multi-threading, filtering, and caching.
        Returns:
          valid_files: A list of text files that pass all filters
          tree_summary: Output of 'tree' command or fallback
        """
        valid_files = []
        tree_summary = self.generate_tree_summary()

        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.process_file, os.path.join(root, file)): file
                for root, _, files in os.walk(self.root_path) for file in files
            }

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    file_path, is_text = result
                    if is_text:
                        valid_files.append(file_path)

        # Ensure cached file count matches valid text files
        cursor.execute("SELECT COUNT(*) FROM file_cache WHERE hash IS NOT NULL")
        cached_file_count = cursor.fetchone()[0]

        logger.debug(f"🔄 Cached file count (valid text files only): {cached_file_count}")
        conn.close()

        logger.info(f"✅ Scanning complete. {len(valid_files)} text files found.")
        return valid_files, tree_summary

    def process_file(self, file_path):
        """
        Process a file and determine if it should be included or skipped.
        Returns (file_path, True) if it is a valid text file that passes all checks,
        otherwise returns None.
        """
        file_path = os.path.abspath(file_path)  # Ensure absolute paths for consistency

        # 1. Skip excluded patterns
        if any(pattern in file_path for pattern in self.exclude_patterns):
            logger.debug(f"❌ Skipping excluded file: {file_path}")
            return None

        # 2. If docs_only is True, skip files that are not recognized as documentation
        if self.docs_only and not self._is_documentation_file(file_path):
            logger.debug(f"❌ Skipping non-doc file (docs_only): {file_path}")
            return None

        # 3. Skip files not in include list (if include_patterns is set)
        if self.include_patterns and not any(file_path.endswith(p) for p in self.include_patterns):
            logger.debug(f"❌ Skipping file not in include list: {file_path}")
            return None

        # 4. Skip oversized files
        if self.size_limit and os.path.getsize(file_path) > self.size_limit:
            logger.debug(f"⚠️ Skipping oversized file: {file_path}")
            return None

        # 5. If auto_filter, do an extra quick check for known unneeded patterns
        if self.auto_filter and self._auto_filter_file(file_path):
            return None

        # 6. Skip non-text files
        if not self.is_text_file(file_path):
            return None

        # 7. Check cache
        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM file_cache WHERE path = ?", (file_path,))
        cached_entry = cursor.fetchone()

        file_hash = self.get_file_hash(file_path)
        if cached_entry and cached_entry[0] == file_hash:
            logger.debug(f"⚡ Skipping unchanged file (cached): {file_path}")
            conn.close()
            return (file_path, True)

        if not file_hash:
            conn.close()
            return None  # Skip if hashing failed

        # 8. Update cache with new/changed file
        cursor.execute("REPLACE INTO file_cache (path, hash) VALUES (?, ?)", (file_path, file_hash))
        conn.commit()
        conn.close()

        return (file_path, True)  # Valid text file
