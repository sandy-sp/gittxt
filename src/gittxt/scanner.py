import asyncio
from pathlib import Path
from typing import List, Tuple, Optional

from gittxt.logger import Logger
from gittxt.utils import filetype_utils, pattern_utils
from gittxt.utils.tree_utils import generate_tree

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

logger = Logger.get_logger(__name__)


class Scanner:
    """
    Scans directories, filters files by type, and returns valid files.
    Uses asyncio to process files concurrently, falling back to a 
    synchronous approach if async execution is unavailable.
    """

    def __init__(
        self,
        root_path: Path,
        include_patterns: List[str],
        exclude_patterns: List[str],
        size_limit: Optional[int],
        file_types: List[str],
        progress: bool = False,
    ):
        """
        :param root_path: Base directory for scanning (local clone or local path).
        :param include_patterns: List of file-patterns to include (e.g. [".py", ".md"]).
        :param exclude_patterns: List of file-patterns/folders to exclude (e.g. ["node_modules"]).
        :param size_limit: Maximum file size in bytes (None for no limit).
        :param file_types: List of file types to include (e.g. ["code", "docs"] or ["all"]).
        :param progress: Whether to display a progress bar during scanning.
        """
        self.root_path = Path(root_path).resolve()
        self.include_patterns = pattern_utils.normalize_patterns(include_patterns)
        self.exclude_patterns = pattern_utils.normalize_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.file_types = set(file_types)
        self.progress = progress

    def scan_directory(self) -> Tuple[List[Path], str]:
        """
        Public method that attempts to run the asynchronous file scan,
        then falls back to a synchronous scan if asyncio fails.
        
        :return: (valid_files, tree_summary)
                 valid_files: a list of Paths that passed filtering
                 tree_summary: a string representing the directory structure
        """
        try:
            # Attempt the async approach by running an event loop
            return asyncio.run(self._scan_directory_async())
        except RuntimeError as exc:
            logger.warning(f"⚠️ Async scan failed due to: {exc}. Falling back to sync mode.")
            return self._scan_directory_sync()

    async def _scan_directory_async(self) -> Tuple[List[Path], str]:
        """
        Asynchronous approach to scanning. Files are processed concurrently
        via asyncio.to_thread, with an optional progress bar.

        :return: (valid_files, tree_summary)
        """
        all_paths = list(self.root_path.rglob("*"))
        logger.debug(f"Found {len(all_paths)} total items under {self.root_path}")

        # Create a TQDM progress bar if enabled and available
        bar = None
        if self.progress and tqdm is not None:
            bar = tqdm(
                total=len(all_paths),
                desc="Scanning files",
                unit="file",
                dynamic_ncols=True
            )

        # For each file, create an async task
        tasks = []
        for path in all_paths:
            tasks.append(asyncio.create_task(self._process_path_async(path, bar)))

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)
        valid_files = [res for res in results if res is not None]

        # Close progress bar
        if bar:
            bar.close()

        logger.info(f"✅ Scanned {len(valid_files)} valid files (async).")
        tree_summary = generate_tree(self.root_path)
        return valid_files, tree_summary

    async def _process_path_async(self, file_path: Path, bar) -> Optional[Path]:
        """
        Coroutine that processes a single file path. Uses asyncio.to_thread
        to run the synchronous checks (file filters) in a background thread.
        """
        # If it's not even a file, skip right away (and still update the bar)
        if not file_path.is_file():
            if bar:
                bar.update(1)
            return None

        # Perform all filtering in a worker thread
        result = await asyncio.to_thread(self._check_file_filters, file_path)

        # Update progress
        if bar:
            bar.update(1)

        return result

    def _check_file_filters(self, file_path: Path) -> Optional[Path]:
        """
        Synchronous filter checks: size, include/exclude patterns, file type.
        Returns the file path if valid, else None.
        """
        if not self._passes_filters(file_path):
            return None
        if not self._passes_filetype_filter(file_path):
            return None
        return file_path.resolve()

    def _scan_directory_sync(self) -> Tuple[List[Path], str]:
        """
        Fallback synchronous method, matching the original approach.
        If the async scan fails or isn't desired, we use this method.
        
        :return: (valid_files, tree_summary)
        """
        valid_files = []
        files = list(self.root_path.rglob("*"))

        # Use TQDM if requested
        iter_files = files
        if self.progress and tqdm is not None:
            iter_files = tqdm(files, desc="Scanning files (sync)", unit="file", dynamic_ncols=True)

        for file in iter_files:
            if not file.is_file():
                continue
            if not self._passes_filters(file):
                continue
            if not self._passes_filetype_filter(file):
                continue
            valid_files.append(file.resolve())

        logger.info(f"✅ Scanned {len(valid_files)} valid files (sync).")
        tree_summary = generate_tree(self.root_path)
        return valid_files, tree_summary

    def _passes_filters(self, file_path: Path) -> bool:
        """
        Check exclude and include patterns, plus size limit.
        """
        # Exclude pattern
        if pattern_utils.match_exclude(file_path, self.exclude_patterns):
            return False

        # Include pattern (if provided)
        if self.include_patterns and not pattern_utils.match_include(file_path, self.include_patterns):
            return False

        # Size limit
        if self.size_limit and file_path.stat().st_size > self.size_limit:
            return False

        return True

    def _passes_filetype_filter(self, file_path: Path) -> bool:
        """
        Check if this file's detected type is in self.file_types 
        or if self.file_types == {"all"} then all are allowed.
        """
        if self.file_types == {"all"}:
            return True

        detected_type = filetype_utils.classify_file(file_path)
        return detected_type in self.file_types
