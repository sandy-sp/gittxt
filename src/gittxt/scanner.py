import os
import mimetypes
import sqlite3
import asyncio
import aiofiles
import hashlib
import subprocess
from gittxt.logger import Logger
from gittxt.config import ConfigManager
from gittxt.utils import get_file_extension, normalize_path  

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
        :param docs_only: If True, only documentation files are processed.
        :param auto_filter: If True, automatically skip common unwanted/binary file types.
        """
        self.root_path = normalize_path(root_path)
        self.include_patterns = self._parse_patterns(include_patterns)
        self.exclude_patterns = self._parse_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.docs_only = docs_only
        self.auto_filter = auto_filter
        self.config = ConfigManager.load_config()

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

    async def read_file_content(self, file_path):
        """Read file content asynchronously."""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return await f.readlines()
        except Exception as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return []

    def _parse_patterns(self, patterns):
        """Convert comma-separated string patterns into a list of stripped patterns."""
        if isinstance(patterns, str):
            return [p.strip() for p in patterns.split(",")]
        return patterns if patterns else []

    def _is_documentation_file(self, file_path):
        """Check if a file is documentation based on its extension and location."""
        doc_extensions = {".md", ".rst", ".txt"}
        basename = os.path.basename(file_path).lower()
        ext = get_file_extension(basename)
        
        if ext in doc_extensions or basename.startswith(("readme", "license", "contributing", "changelog")):
            return True
        
        return "docs" in normalize_path(file_path).split(os.sep)

    def _auto_filter_file(self, file_path):
        """Skip common unwanted or binary file types automatically."""
        auto_exclude_ext = {
            ".log", ".gz", ".tar", ".jpg", ".jpeg", ".png", ".csv", ".pdf", ".doc", ".docx"
        }
        return get_file_extension(file_path).lower() in auto_exclude_ext

    def is_text_file(self, file_path):
        """Determine if a file is text-based using MIME type detection."""
        binary_extensions = {
            ".mp4", ".avi", ".mov", ".tar.gz", ".zip", ".exe", ".bin", ".jpeg", ".png", ".gif", ".pdf"
        }
        if file_path.endswith(tuple(binary_extensions)):
            return False

        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type and mime_type.startswith("text")

    def generate_tree_summary(self):
        """Generate a folder structure summary using 'tree' command (if available)."""
        try:
            return subprocess.check_output(["tree", self.root_path], text=True)
        except FileNotFoundError:
            return "⚠️ Tree command not available."
        except subprocess.SubprocessError as e:
            return f"⚠️ Error generating repository structure: {e}"

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

    async def scan_directory(self):
        """Scan directory asynchronously using filters and caching."""
        valid_files = []
        tree_summary = self.generate_tree_summary()
        
        for root, _, files in os.walk(self.root_path):
            for file in files:
                file_path = os.path.join(root, file)
                result = await self.process_file(file_path)
                if result:
                    valid_files.append(result)

        logger.info(f"✅ Scanning complete. {len(valid_files)} text files found.")
        return valid_files, tree_summary

    async def process_file(self, file_path):
        """Process a file and determine if it should be included or skipped."""
        file_path = normalize_path(file_path)
        
        if any(pattern in file_path for pattern in self.exclude_patterns):
            return None
        if self.docs_only and not self._is_documentation_file(file_path):
            return None
        if self.include_patterns and not file_path.endswith(tuple(self.include_patterns)):
            return None
        if self.size_limit and os.path.getsize(file_path) > self.size_limit:
            return None
        if self.auto_filter and self._auto_filter_file(file_path):
            return None
        if not self.is_text_file(file_path):
            return None
        
        file_hash = hashlib.sha256((await self.read_file_content(file_path)).encode()).hexdigest()
        return file_path, file_hash
    