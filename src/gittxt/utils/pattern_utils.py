from pathlib import Path
from typing import List
import fnmatch
from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)

def normalize_patterns(patterns: List[str]) -> List[str]:
    """
    Normalize patterns to lower-case and strip whitespace.
    """
    return [p.strip().lower() for p in patterns if p.strip()]

def match_exclude_dir(path: Path, exclude_dirs: List[str]) -> bool:
    """
    Check if the path is inside any of the excluded directories.
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
            logger.debug(f"🛑 Skipped (size limit {file_path.stat().st_size} > {size_limit}): {file_path}")
        return False

    # If include_patterns are specified but the file doesn't match any, log and skip.
    if verbose and hasattr(file_path, "match"):
        matched = any(file_path.match(pat) for pat in [])
        if not matched:
            logger.debug(f"File {file_path} did not match any include pattern (if any specified).")
    return True