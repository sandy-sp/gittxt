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
    """Scans directories, filters files by type, and returns valid files."""

    def __init__(
        self,
        root_path: Path,
        include_patterns: List[str],
        exclude_patterns: List[str],
        size_limit: Optional[int],
        file_types: List[str],
        progress: bool = False,
    ):
        self.root_path = Path(root_path).resolve()
        self.include_patterns = pattern_utils.normalize_patterns(include_patterns)
        self.exclude_patterns = pattern_utils.normalize_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.file_types = set(file_types)
        self.progress = progress

    def scan_directory(self) -> Tuple[List[Path], str]:
        """Run scan with async or sync fallback. Returns valid files and directory tree."""
        try:
            valid_files = asyncio.run(self._scan_directory_async())
            logger.info(f"✅ Scanned {len(valid_files)} valid files (async).")
        except RuntimeError as exc:
            logger.warning(f"⚠️ Async scan failed due to: {exc}. Falling back to sync mode.")
            valid_files = self._scan_directory_sync()
            logger.info(f"✅ Scanned {len(valid_files)} valid files (sync).")

        # Generate tree once after filtering
        tree_summary = generate_tree(self.root_path)
        return valid_files, tree_summary

    async def _scan_directory_async(self) -> List[Path]:
        """Asynchronous scanning using to_thread for I/O bound operations."""
        all_paths = list(self.root_path.rglob("*"))
        logger.debug(f"Found {len(all_paths)} total items under {self.root_path}")

        bar = self._init_progress_bar(len(all_paths), "Scanning files (async)")

        valid_files = []
        tasks = []
        for path in all_paths:
            tasks.append(self._process_path_async(path, bar))

        results = await asyncio.gather(*tasks)
        valid_files = [file for file in results if file is not None]

        if bar:
            bar.close()

        return valid_files

    async def _process_path_async(self, file_path: Path, bar) -> Optional[Path]:
        if not file_path.is_file():
            self._progress_update(bar)
            return None
        result = await asyncio.to_thread(self._check_file_filters, file_path)
        self._progress_update(bar)
        return result

    def _scan_directory_sync(self) -> List[Path]:
        """Synchronous fallback scanner."""
        valid_files = []
        files = list(self.root_path.rglob("*"))
        bar = self._init_progress_bar(len(files), "Scanning files (sync)")

        for file in files:
            if not file.is_file():
                self._progress_update(bar)
                continue
            result = self._check_file_filters(file)
            if result:
                valid_files.append(result)
            self._progress_update(bar)

        if bar:
            bar.close()
        return valid_files

    def _check_file_filters(self, file_path: Path) -> Optional[Path]:
        """Core filter checks."""
        if not self._passes_filters(file_path):
            return None
        if not self._passes_filetype_filter(file_path):
            return None
        return file_path.resolve()

    def _passes_filters(self, file_path: Path) -> bool:
        if pattern_utils.match_exclude(file_path, self.exclude_patterns):
            return False
        if self.include_patterns and not pattern_utils.match_include(file_path, self.include_patterns):
            return False
        if self.size_limit and file_path.stat().st_size > self.size_limit:
            return False
        return True

    def _passes_filetype_filter(self, file_path: Path) -> bool:
        return True if self.file_types == {"all"} else filetype_utils.classify_file(file_path) in self.file_types

    def _init_progress_bar(self, total, desc):
        if self.progress and tqdm:
            return tqdm(total=total, desc=desc, unit="file", dynamic_ncols=True)
        return None

    def _progress_update(self, bar):
        if bar:
            bar.update(1)
