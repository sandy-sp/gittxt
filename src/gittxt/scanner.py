from pathlib import Path
import mimetypes
import sqlite3
import concurrent.futures
import hashlib
from gittxt.logger import Logger
from gittxt.utils.tree_utils import generate_tree

logger = Logger.get_logger(__name__)

class Scanner:
    """
    Handles scanning of local directories and filtering based on file type and patterns.
    Now supports optional 'docs_only' and 'auto_filter' toggles for advanced filtering.
    """

    BASE_CACHE_DIR = (Path(__file__).parent / "../gittxt-outputs/cache").resolve()
    CACHE_DB = BASE_CACHE_DIR / "scan_cache.db"

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
        :param docs_only: If True, only documentation files (README, .md, .rst, .txt, etc.) are processed.
        :param auto_filter: If True, automatically skip common unwanted/binary file types.
        """
        self.root_path = Path(root_path).resolve()
        self.include_patterns = self._parse_patterns(include_patterns)
        self.exclude_patterns = self._parse_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.docs_only = docs_only
        self.auto_filter = auto_filter

        self._initialize_cache()

    def _initialize_cache(self):
        """Ensure SQLite cache database is set up for incremental scanning."""
        self.BASE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
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
        """Clear the cache database."""
        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM file_cache")
        conn.commit()
        conn.close()
        logger.info("🗑️ Cache cleared.")

    def _parse_patterns(self, patterns):
        if isinstance(patterns, str):
            return [p.strip() for p in patterns.split(",")]
        return patterns if patterns else []

    def _is_documentation_file(self, file_path: Path):
        basename = file_path.name.lower()
        ext = file_path.suffix.lower()

        doc_extensions = {".md", ".rst", ".txt"}
        if ext in doc_extensions:
            return True

        doc_filenames = {"readme", "license", "contributing", "changelog"}
        if any(basename.startswith(keyword) for keyword in doc_filenames):
            return True

        if "docs" in file_path.parts:
            return True

        return False

    def _auto_filter_file(self, file_path: Path):
        auto_exclude_ext = {".log", ".gz", ".tar", ".jpg", ".jpeg", ".png", ".csv", ".pdf", ".doc", ".docx"}
        if file_path.suffix.lower() in auto_exclude_ext:
            logger.debug(f"❌ Auto-filter skipping file: {file_path}")
            return True
        return False

    def is_text_file(self, file_path: Path):
        binary_extensions = {".mp4", ".avi", ".mov", ".tar.gz", ".zip", ".exe", ".bin", ".jpeg", ".png", ".gif", ".pdf"}
        if any(str(file_path).endswith(ext) for ext in binary_extensions):
            logger.debug(f"❌ Skipping binary file based on extension: {file_path}")
            return False

        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            return False

        if mime_type.startswith("text"):
            return True

        logger.debug(f"❌ Skipping non-text file (MIME: {mime_type}): {file_path}")
        return False

    def generate_tree_summary(self):
        tree_str = generate_tree(self.root_path)
        return tree_str or "⚠️ No files found or directory empty."

    def get_file_hash(self, file_path: Path):
        try:
            hasher = hashlib.sha256()
            with file_path.open("rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"❌ Error hashing file {file_path}: {e}")
            return None

    def scan_directory(self):
        valid_files = []
        tree_summary = self.generate_tree_summary()

        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.process_file, file_path): file_path
                for file_path in self.root_path.rglob("*") if file_path.is_file()
            }

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    file_path, is_text = result
                    if is_text:
                        valid_files.append(str(file_path))

        cursor.execute("SELECT COUNT(*) FROM file_cache WHERE hash IS NOT NULL")
        cached_file_count = cursor.fetchone()[0]
        logger.debug(f"🔄 Cached file count (valid text files only): {cached_file_count}")
        conn.close()

        logger.info(f"✅ Scanning complete. {len(valid_files)} text files found.")
        return valid_files, tree_summary

    def process_file(self, file_path: Path):
        file_path = file_path.resolve()

        if any(pattern in str(file_path) for pattern in self.exclude_patterns):
            logger.debug(f"❌ Skipping excluded file: {file_path}")
            return None

        if self.docs_only and not self._is_documentation_file(file_path):
            logger.debug(f"❌ Skipping non-doc file (docs_only): {file_path}")
            return None

        if self.include_patterns and not any(str(file_path).endswith(p) for p in self.include_patterns):
            logger.debug(f"❌ Skipping file not in include list: {file_path}")
            return None

        if self.size_limit and file_path.stat().st_size > self.size_limit:
            logger.debug(f"⚠️ Skipping oversized file: {file_path}")
            return None

        if self.auto_filter and self._auto_filter_file(file_path):
            return None

        if not self.is_text_file(file_path):
            return None

        conn = sqlite3.connect(self.CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM file_cache WHERE path = ?", (str(file_path),))
        cached_entry = cursor.fetchone()

        file_hash = self.get_file_hash(file_path)
        if cached_entry and cached_entry[0] == file_hash:
            logger.debug(f"⚡ Skipping unchanged file (cached): {file_path}")
            conn.close()
            return (file_path, True)

        if not file_hash:
            conn.close()
            return None

        cursor.execute("REPLACE INTO file_cache (path, hash) VALUES (?, ?)", (str(file_path), file_hash))
        conn.commit()
        conn.close()

        return (file_path, True)
