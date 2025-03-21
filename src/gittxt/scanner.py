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
    """Scans directories, applies filters, and returns valid files with async batching."""

    def __init__(
        self,
        root_path: Path,
        include_patterns: List[str],
        exclude_patterns: List[str],
        size_limit: Optional[int],
        file_types: List[str],
        progress: bool = False,
        batch_size: int = 50,
        tree_depth: Optional[int] = None,
    ):
        self.root_path = root_path.resolve()
        self.include_patterns = pattern_utils.normalize_patterns(include_patterns)
        self.exclude_patterns = pattern_utils.normalize_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.file_types = set(file_types)
        self.progress = progress
        self.batch_size = batch_size
        self.tree_depth = tree_depth # or config.get("tree_depth", None)

    def scan_directory(self) -> Tuple[List[Path], str]:
        """Run scan with async or sync fallback. Returns valid files and directory tree."""
        try:
            valid_files = asyncio.run(self._scan_directory_async())
            logger.info(f"✅ Async scan complete: {len(valid_files)} valid files found.")
        except RuntimeError as exc:
            logger.warning(f"⚠️ Async scan failed due to: {exc}. Falling back to sync mode.")
            valid_files = self._scan_directory_sync()
            logger.info(f"✅ Sync scan complete: {len(valid_files)} valid files found.")
        logger.info("🌳 Generating directory tree after scan...")
        tree_summary = generate_tree(self.root_path, max_depth=self.tree_depth)
        return valid_files, tree_summary

    async def _scan_directory_async(self) -> List[Path]:
        """Batch async scanning using asyncio.gather + to_thread."""
        all_paths = list(self.root_path.rglob("*"))
        logger.debug(f"📂 Found {len(all_paths)} total items under {self.root_path}")

        dynamic_batch_size = min(self.batch_size, max(10, len(all_paths) // 20))

        bar = self._init_progress_bar(len(all_paths), "Scanning files (async batch)")

        valid_files = []
        for i in range(0, len(all_paths), dynamic_batch_size):
            batch = all_paths[i: i + dynamic_batch_size]
            batch_results = await asyncio.gather(*[self._process_batch_file(path, bar) for path in batch])
            valid_files.extend([res for res in batch_results if res is not None])

        if bar:
            bar.close()

        return valid_files

    async def _process_batch_file(self, file_path: Path, bar) -> Optional[Path]:
        if not file_path.is_file():
            self._progress_update(bar)
            return None

        try:
            result = await asyncio.to_thread(self._check_file_filters, file_path)
        except Exception as e:
            logger.warning(f"❌ Skipped {file_path}: {e}")
            result = None

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
            logger.debug(f"🛑 Excluded by pattern: {file_path}")
            return False
        if self.include_patterns and not pattern_utils.match_include(file_path, self.include_patterns):
            return False
        if self.size_limit and file_path.stat().st_size > self.size_limit:
            logger.debug(f"🛑 Excluded by size limit: {file_path}")
            return False
        return True

    def _passes_filetype_filter(self, file_path: Path) -> bool:
        # If "all" mode, accept everything.
        if self.file_types == {"all"}:
            return True
        classification = filetype_utils.classify_file(file_path)
        return classification in self.file_types

    def _init_progress_bar(self, total, desc):
        if self.progress and tqdm and total > 5:
            return tqdm(total=total, desc=desc, unit="file", dynamic_ncols=True)
        return None

    def _progress_update(self, bar):
        if bar:
            bar.update(1)
