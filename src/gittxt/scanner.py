from pathlib import Path
from typing import List, Tuple
from gittxt.logger import Logger
from gittxt.utils import filetype_utils
from gittxt.utils import pattern_utils
from gittxt.utils.tree_utils import generate_tree

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

logger = Logger.get_logger(__name__)


class Scanner:
    """
    Scans directories, filters files by type, and returns valid files.
    """

    def __init__(
        self,
        root_path: Path,
        include_patterns: List[str],
        exclude_patterns: List[str],
        size_limit: int,
        file_types: List[str],
        progress: bool = False,
    ):
        self.root_path = Path(root_path).resolve()
        self.include_patterns = pattern_utils.normalize_patterns(include_patterns)
        self.exclude_patterns = pattern_utils.normalize_patterns(exclude_patterns)
        self.size_limit = size_limit
        self.file_types = set(file_types)
        self.progress = progress

    def _passes_filters(self, file_path: Path) -> bool:
        if pattern_utils.match_exclude(file_path, self.exclude_patterns):
            return False
        if self.include_patterns and not pattern_utils.match_include(
            file_path, self.include_patterns
        ):
            return False
        if self.size_limit and file_path.stat().st_size > self.size_limit:
            return False
        return True

    def _passes_filetype_filter(self, file_path: Path) -> bool:
        detected_type = filetype_utils.classify_file(file_path)
        if self.file_types == {"all"}:
            return True
        return detected_type in self.file_types

    def scan_directory(self) -> Tuple[List[Path], str]:
        """
        Scans directory and filters files based on type and patterns.
        Returns:
            - List of valid file paths.
            - Directory tree string (for summary).
        """
        valid_files = []
        files = list(self.root_path.rglob("*"))

        iter_files = (
            tqdm(files, desc="Scanning files") if self.progress and tqdm else files
        )

        for file in iter_files:
            if not file.is_file():
                continue
            if not self._passes_filters(file):
                continue
            if not self._passes_filetype_filter(file):
                continue
            valid_files.append(file.resolve())

        logger.info(f"✅ Scanned {len(valid_files)} valid files.")
        tree_summary = generate_tree(self.root_path)
        return valid_files, tree_summary
