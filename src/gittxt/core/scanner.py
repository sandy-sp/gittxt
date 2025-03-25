import asyncio
from pathlib import Path
from typing import List, Optional
from gittxt.core.logger import Logger
from gittxt.utils import pattern_utils, filetype_utils
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

logger = Logger.get_logger(__name__)

class Scanner:
    """
    Scans directories, applies directory exclusion and size filters,
    then classifies files as TEXTUAL or NON-TEXTUAL.
    """

    def __init__(
        self,
        root_path: Path,
        exclude_dirs: List[str],
        size_limit: Optional[int],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        progress: bool = False,
        batch_size: int = 50,
        verbose: bool = False,
    ):
        self.root_path = root_path.resolve()
        self.exclude_dirs = pattern_utils.normalize_patterns(exclude_dirs)
        self.size_limit = size_limit
        self.progress = progress
        self.batch_size = batch_size
        self.verbose = verbose
        self.accepted_files = []
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []

    async def _process_single_file(self, file_path: Path):
        if not file_path.is_file():
            return
        if not pattern_utils.passes_all_filters(file_path, self.exclude_dirs, self.size_limit, self.verbose):
            return
        primary, reason = filetype_utils.classify_simple(file_path)

        # Exclude hard-coded non-textuals (cannot be forced in)
        if primary != "TEXTUAL":
            if self.verbose:
                logger.debug(f"🛑 Skipped (non-textual: {reason}): {file_path}")
            return

        # Apply custom exclude-patterns
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                if self.verbose:
                    logger.debug(f"🛑 Skipped (exclude pattern): {file_path}")
                return

        # Apply include-patterns (only if specified)
        if self.include_patterns:
            if not any(file_path.match(pat) for pat in self.include_patterns):
                if self.verbose:
                    logger.debug(f"🛑 Skipped (not in include patterns): {file_path}")
                return

        # If passed all filters
        self.accepted_files.append(file_path.resolve())

    async def scan_directory(self) -> List[Path]:
        all_paths = [
            p for p in self.root_path.rglob("*")
            if not pattern_utils.match_exclude_dir(p, self.exclude_dirs)
        ]
        logger.debug(f"📂 Found {len(all_paths)} total items after pruning excluded dirs")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            transient=True
        ) as progress_bar:
            task = progress_bar.add_task("Scanning repository files", total=len(all_paths))
            semaphore = asyncio.Semaphore(100)

            async def limited_process(file_path: Path):
                async with semaphore:
                    await self._process_single_file(file_path)
                    progress_bar.update(task, advance=1)

            await asyncio.gather(*[limited_process(f) for f in all_paths])
            progress_bar.update(task, completed=len(all_paths))

        logger.info(f"✅ Scan complete: {len(self.accepted_files)} textual files accepted.")
        return self.accepted_files
