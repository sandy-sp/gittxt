import asyncio
from pathlib import Path
from typing import List, Tuple, Optional

from gittxt.logger import Logger
from gittxt.utils import pattern_utils, filetype_utils
from gittxt.utils.tree_utils import generate_tree

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

logger = Logger.get_logger(__name__)

class Scanner:
    """Scans directories, applies filters, and categorizes files into TEXTUAL / NON-TEXTUAL."""

    def __init__(
        self,
        root_path: Path,
        include_patterns: List[str],
        exclude_patterns: List[str],
        size_limit: Optional[int],
        file_types: List[str],  # accepts "all" or ["TEXTUAL", "NON-TEXTUAL"]
        progress: bool = False,
        batch_size: int = 50,
        tree_depth: Optional[int] = None,
        verbose: bool = False,
    ):
        self.root_path = root_path.resolve()
        self.include_patterns = pattern_utils.normalize_patterns(include_patterns)
        self.exclude_patterns = pattern_utils.normalize_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.file_types = set(file_types)
        self.progress = progress
        self.batch_size = batch_size
        self.tree_depth = tree_depth
        self.verbose = verbose

        # Buckets
        self.textual = []
        self.non_textual = []

    def scan_directory(self) -> Tuple[List[Path], str]:
        try:
            asyncio.run(self._scan_directory_async())
            logger.info(f"✅ Async scan complete: {len(self.textual) + len(self.non_textual)} files processed.")
        except RuntimeError as exc:
            logger.warning(f"⚠️ Async scan failed: {exc}. Falling back to sync.")
            self._scan_directory_sync()
            logger.info(f"✅ Sync scan complete: {len(self.textual) + len(self.non_textual)} files processed.")

        logger.info("🌳 Generating directory tree...")
        tree_summary = generate_tree(self.root_path, max_depth=self.tree_depth)
        return self.textual + self.non_textual, tree_summary

    async def _scan_directory_async(self):
        all_paths = list(self.root_path.rglob("*"))
        logger.debug(f"📂 Found {len(all_paths)} total items")

        dynamic_batch_size = min(self.batch_size, max(50, len(all_paths) // 10))
        bar = self._init_progress_bar(len(all_paths), "Scanning files (async batch)")

        tasks = []
        for i in range(0, len(all_paths), dynamic_batch_size):
            batch = all_paths[i:i + dynamic_batch_size]
            tasks.extend([self._process_batch_file(path, bar) for path in batch])

        await asyncio.gather(*tasks)
        if bar: bar.close()

    def _scan_directory_sync(self):
        files = list(self.root_path.rglob("*"))
        bar = self._init_progress_bar(len(files), "Scanning files (sync)")

        for file in files:
            if not file.is_file():
                self._progress_update(bar)
                continue
            self._process_single_file(file)
            self._progress_update(bar)

        if bar: bar.close()

    async def _process_batch_file(self, file_path: Path, bar):
        if not file_path.is_file():
            self._progress_update(bar)
            return
        await asyncio.to_thread(self._process_single_file, file_path)
        self._progress_update(bar)

    def _process_single_file(self, file_path: Path):
        if not self._passes_filters(file_path):
            return

        primary, sub = filetype_utils.classify_simple(file_path)

        if primary == "TEXTUAL":
            self.textual.append(file_path.resolve())
        elif primary == "NON-TEXTUAL":
            self.non_textual.append(file_path.resolve())

    def _passes_filters(self, file_path: Path) -> bool:
        if pattern_utils.match_exclude(file_path, self.exclude_patterns):
            if self.verbose:
                logger.debug(f"🛑 Excluded by pattern: {file_path}")
            return False
        if self.include_patterns and not pattern_utils.match_include(file_path, self.include_patterns):
            return False
        if self.size_limit and file_path.stat().st_size > self.size_limit:
            if self.verbose:
                logger.debug(f"🛑 Excluded by size limit: {file_path}")
            return False
        return True

    def _init_progress_bar(self, total, desc):
        if self.progress and tqdm and total >= 1:
            return tqdm(total=total, desc=desc, unit="file", dynamic_ncols=True)
        return None

    def _progress_update(self, bar):
        if bar:
            bar.update(1)
