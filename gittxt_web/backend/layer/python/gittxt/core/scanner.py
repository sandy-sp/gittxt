import asyncio
from pathlib import Path
from typing import List, Optional
from gittxt.utils import pattern_utils
from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager
from gittxt.utils import filetype_utils

logger = Logger.get_logger(__name__)


class Scanner:
    """
    Scans directories for textual files, ignoring non-textual ones.
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
        use_ignore_file: bool = False,
    ):
        self.root_path = root_path.resolve()
        self.exclude_dirs = list(exclude_dirs or [])
        self.size_limit = size_limit
        self.include_patterns = list(include_patterns) if include_patterns else []
        self.exclude_patterns = list(exclude_patterns) if exclude_patterns else []
        self.progress = progress
        self.batch_size = batch_size
        self.verbose = verbose
        self.accepted_files = []
        self.skipped_files = []
        self.non_textual_files = []

        if use_ignore_file:
            ignore_file = self.root_path / ".gittxtignore"
            if ignore_file.exists():
                from gittxt.utils.ignore_utils import parse_ignore_file

                patterns = parse_ignore_file(ignore_file)
                self.exclude_patterns.extend(patterns)
                logger.debug(f"📁 Merged {len(patterns)} patterns from .gittxtignore")

    async def scan_directory(self) -> List[Path]:
        """
        Async-friendly method to gather textual files under root_path,
        skipping excluded directories and large files.
        Returns:
        Tuple[List[Path], List[Path]]: Accepted textual files and non-textual files
        """
        all_items = [
            p
            for p in self.root_path.rglob("*")
            if not pattern_utils.match_exclude_dir(p, self.exclude_dirs)
        ]
        logger.debug(f"📂 Found {len(all_items)} items after exclude_dir filtering.")
        config = ConfigManager.load_config()
        concurrency = config.get("scan_concurrency", 200)
        semaphore = asyncio.Semaphore(concurrency)

        async def process_path(path: Path):
            async with semaphore:
                try:
                    await self._process_single(path)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"❌ Error processing file {path}: {e}")
                    self._record_skip(path, f"processing error: ({e})")

        await asyncio.gather(*[process_path(p) for p in all_items])
        # 📊 Post-scan summary
        accepted = len(self.accepted_files)
        skipped = len(self.skipped_files)
        nontext = len(self.non_textual_files)

        if accepted == 0:
            logger.warning("⚠️ No textual files were accepted after filtering.")

        logger.info(
            f"✅ Scan complete: {accepted} accepted, {nontext} non-textual, {skipped} skipped."
        )
        return self.accepted_files, self.non_textual_files

    def _record_skip(self, path: Path, reason: str):
        resolved = path.resolve()
        if all(resolved != p.resolve() for p, _ in self.skipped_files):
            self.skipped_files.append((resolved, reason))

    async def _process_single(self, path: Path):
        ext = path.suffix.lower() if path.suffix else ""
        if not isinstance(ext, str):
            self._record_skip(path, "invalid extension")
            return

        if not path.is_file():
            return

        label = filetype_utils.classify_file(path)

        if not pattern_utils.passes_all_filters(
            path, self.exclude_dirs, self.size_limit, self.verbose
        ):
            self._record_skip(path, "filtered by size or dir")
            return

        if self.exclude_patterns and any(path.match(p) for p in self.exclude_patterns):
            if self.verbose:
                logger.debug(f"🛑 Skipped by exclude pattern: {path}")
            self._record_skip(path, "exclude pattern")
            return

        if self.include_patterns and not any(
            path.match(p) for p in self.include_patterns
        ):
            if self.verbose:
                logger.debug(f"🛑 Skipped by not matching include pattern: {path}")
            self._record_skip(path, "not in include patterns")
            return

        if label != "TEXTUAL":
            self.non_textual_files.append(path)
            if self.include_patterns and any(
                path.match(p) for p in self.include_patterns
            ):
                logger.warning(
                    f"⚠️ Skipped non-textual file matched by --include: {path}"
                )
            if self.verbose:
                logger.debug(f"🛑 Skipped non-textual file: {path}")
            self._record_skip(path, f"non-textual ({label})")
            return

        self.accepted_files.append(path)
