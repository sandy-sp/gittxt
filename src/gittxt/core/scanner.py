import asyncio
from pathlib import Path
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager
from gittxt.utils import pattern_utils, filetype_utils
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT

logger = Logger.get_logger(__name__)

class Scanner:
    """
    Scans directories for textual files, ignoring non-textual.
    Applies folder and size excludes. Optionally merges .gitignore.
    """

    def __init__(
        self,
        root_path: Path,
        exclude_dirs: Optional[List[str]] = None,
        size_limit: Optional[int] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        progress: bool = False,
        batch_size: int = 50,
        verbose: bool = False,
    ):
        self.root_path = root_path.resolve()
        self.exclude_dirs = exclude_dirs or []
        self.size_limit = size_limit
        self.include_patterns = list(include_patterns) if include_patterns else []
        self.exclude_patterns = list(exclude_patterns) if exclude_patterns else []
        self.progress = progress
        self.batch_size = batch_size
        self.verbose = verbose
        self.accepted_files = []

    async def scan_directory(self) -> List[Path]:
        """
        Async-friendly method to gather textual files under root_path,
        skipping excluded directories and large files.
        """
        all_items = [p for p in self.root_path.rglob("*") if not pattern_utils.match_exclude_dir(p, self.exclude_dirs)]
        logger.debug(f"📂 Found {len(all_items)} items after exclude_dir filtering.")
        config = ConfigManager.load_config()
        concurrency = config.get("scan_concurrency", 200)
        semaphore = asyncio.Semaphore(concurrency)

        # Setup progress bar if needed
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            transient=True
        ) as progress_bar:
            task_id = progress_bar.add_task("Scanning repository files...", total=len(all_items))

            async def process_path(path: Path):
                async with semaphore:
                    await self._process_single(path)
                    progress_bar.update(task_id, advance=1)

            await asyncio.gather(*[process_path(p) for p in all_items])
            progress_bar.update(task_id, completed=len(all_items))

        return self.accepted_files

    async def _process_single(self, path: Path):
        if not path.is_file():
            return
        if not pattern_utils.passes_all_filters(path, self.exclude_dirs, self.size_limit, self.verbose):
            return

        # Skip excluded patterns
        if self.exclude_patterns and any(path.match(p) for p in self.exclude_patterns):
            if self.verbose:
                logger.debug(f"🛑 Skipped by exclude pattern: {path}")
            return

        # Skip files not matching include patterns
        if self.include_patterns and not any(path.match(p) for p in self.include_patterns):
            if self.verbose:
                logger.debug(f"🛑 Skipped by not matching include pattern: {path}")
            return

        # Validate file type
        label = filetype_utils.classify_file(path)
        if label != "TEXTUAL":
            # Warn if included file is non-textual
            if self.include_patterns and any(path.match(p) for p in self.include_patterns):
                logger.warning(f"⚠️ Skipped non-textual file matched by --include: {path}")
            if self.verbose:
                logger.debug(f"🛑 Skipped non-textual file: {path}")
            return

        self.accepted_files.append(path)
