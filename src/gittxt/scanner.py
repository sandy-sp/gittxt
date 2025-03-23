import asyncio
from pathlib import Path
from typing import List, Tuple, Optional

from gittxt.logger import Logger
from gittxt.utils import pattern_utils, filetype_utils

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
        file_types: List[str],
        progress: bool = False,
        batch_size: int = 50,
        verbose: bool = False,
    ):
        self.root_path = root_path.resolve()
        self.include_patterns = pattern_utils.normalize_patterns(include_patterns)
        self.exclude_patterns = pattern_utils.normalize_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.file_types = set(file_types)
        self.progress = progress
        self.batch_size = batch_size
        self.verbose = verbose

        # Normalize "all" flag
        if "all" in self.file_types:
            self.file_types = {"TEXTUAL", "NON-TEXTUAL"}
        else:
            self.file_types = {"TEXTUAL"} if any(ft in {"code", "docs", "configs", "data"} for ft in file_types) else {"NON-TEXTUAL"}

        self.accepted_files = []

    def scan_directory(self) -> Tuple[List[Path], str]:
        try:
            # Avoid creating coroutine before asyncio.run()
            asyncio.run(self._scan_directory_async())
            logger.info(f"✅ Async scan complete: {len(self.accepted_files)} files processed.")
        except RuntimeError as exc:
            logger.warning(f"⚠️ Async scan fallback: {exc} — switching to sync mode.")
            self._scan_directory_sync()
            logger.info(f"✅ Sync scan complete: {len(self.accepted_files)} files processed.")

        return self.accepted_files, ""  # Tree now handled externally in OutputBuilder

    async def _scan_directory_async(self):
        all_paths = list(self.root_path.rglob("*"))
        logger.debug(f"📂 Found {len(all_paths)} total items")

        dynamic_batch_size = self.batch_size or 100
        if len(all_paths) > 1000:
            dynamic_batch_size = max(self.batch_size, len(all_paths) // 20)

        bar = self._init_progress_bar(len(all_paths), "Scanning files (async batch)")

        # ✅ Concurrency limiter
        semaphore = asyncio.Semaphore(100)  # Max 100 concurrent tasks

        async def limited_process(file_path: Path):
            async with semaphore:
                await self._process_batch_file(file_path, bar)

        tasks = []
        for i in range(0, len(all_paths), dynamic_batch_size):
            batch = all_paths[i:i + dynamic_batch_size]
            tasks.extend([limited_process(path) for path in batch])

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

        primary, _ = filetype_utils.classify_simple(file_path)
        if primary in self.file_types:
            self.accepted_files.append(file_path.resolve())

    def _passes_filters(self, file_path: Path) -> bool:
        return pattern_utils.passes_all_filters(
            file_path,
            self.include_patterns,
            self.exclude_patterns,
            self.size_limit,
            self.verbose
        )

    def _init_progress_bar(self, total, desc):
        if self.progress and tqdm and total >= 1:
            return tqdm(total=total, desc=desc, unit="file", dynamic_ncols=True)
        return None

    def _progress_update(self, bar):
        if bar:
            bar.update(1)
