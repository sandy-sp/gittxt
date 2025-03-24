import asyncio
from pathlib import Path
from typing import List, Optional
from gittxt.logger import Logger
from gittxt.utils import pattern_utils, filetype_utils
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

logger = Logger.get_logger(__name__)

class Scanner:
    """
    Scans directories, applies patterns and size filters,
    categorizes files into TEXTUAL / NON-TEXTUAL groups.
    """

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
        self.file_types = self._normalize_file_types(file_types)
        self.progress = progress
        self.batch_size = batch_size
        self.verbose = verbose
        self.accepted_files = []

    def _normalize_file_types(self, file_types):
        if "all" in file_types:
            return {"TEXTUAL", "NON-TEXTUAL"}
        ft_set = set()
        if any(ft in {"code", "docs", "configs", "data", "csv"} for ft in file_types):
            ft_set.add("TEXTUAL")
        if any(ft in {"image", "media"} for ft in file_types):
            ft_set.add("NON-TEXTUAL")
        return ft_set

    async def scan_directory(self) -> List[Path]:
        """Fully async entry point (no asyncio.run() inside)."""
        all_paths = list(self.root_path.rglob("*"))
        logger.debug(f"📂 Found {len(all_paths)} total items")

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
                    await asyncio.to_thread(self._process_single_file, file_path)
                    progress_bar.update(task, advance=1)

            await asyncio.gather(*[limited_process(f) for f in all_paths])
            progress_bar.update(task, completed=len(all_paths))

        logger.info(f"✅ Scan complete: {len(self.accepted_files)} files accepted.")
        return self.accepted_files

    def _process_single_file(self, file_path: Path):
        if not file_path.is_file():
            return
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
