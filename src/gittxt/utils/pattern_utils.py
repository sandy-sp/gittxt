from pathlib import Path
from typing import List
from gittxt.core.logger import Logger
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT

logger = Logger.get_logger(__name__)

def normalize_patterns(patterns: List[str]) -> List[str]:
    """
    Normalize patterns to lower-case and strip whitespace.
    """
    return [p.strip().lower() for p in patterns if p.strip()]

def match_exclude_dir(path: Path, exclude_dirs: List[str]) -> bool:
    """
    Check if the path (any of its parent folders) is in the list of excluded directories.
    """
    parts = {p.lower() for p in path.parts}
    return any(excl.lower() in parts for excl in exclude_dirs)

def passes_all_filters(file_path: Path, exclude_dirs: List[str], size_limit: int, verbose: bool = False) -> bool:
    """
    Check if file should be included based on directory and size filters.
    """
    if match_exclude_dir(file_path, exclude_dirs):
        if verbose:
            logger.debug(f"🛑 Skipped (excluded dir): {file_path}")
        return False

    if size_limit and file_path.stat().st_size > size_limit:
        if verbose:
            logger.debug(f"🛑 Skipped (size {file_path.stat().st_size} > limit {size_limit}): {file_path}")
        return False

    return True

def should_skip_dir(dirname: str, user_excludes: list = []) -> bool:
    return dirname in EXCLUDED_DIRS_DEFAULT or dirname in user_excludes