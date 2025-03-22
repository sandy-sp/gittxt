from pathlib import Path
from typing import List
import fnmatch
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

def match_include(file_path: Path, include_patterns: List[str]) -> bool:
    """
    Check if the file matches any of the include patterns (e.g., ".py", ".md").
    """
    if not include_patterns:
        return True  # Default to include all if no patterns
    rel_path = str(file_path.relative_to(file_path.anchor)).replace("\\", "/")
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in include_patterns)

def match_exclude(file_path: Path, exclude_patterns: List[str]) -> bool:
    """
    Check if the file should be excluded based on folder or extension.
    """
    rel_path = str(file_path.relative_to(file_path.anchor)).replace("\\", "/")
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns)


def normalize_patterns(patterns: List[str]) -> List[str]:
    """
    Normalize patterns to lower-case and strip whitespace.
    """
    return [p.strip().lower() for p in patterns if p.strip()]


def passes_all_filters(file_path: Path, include_patterns: List[str], exclude_patterns: List[str], size_limit: int, verbose: bool = False) -> bool:
    """
    Centralized filter checker used in Scanner.
    """
    if match_exclude(file_path, exclude_patterns):
        if verbose:
            logger.debug(f"🛑 Excluded by pattern: {file_path}")
        return False
    if include_patterns and not match_include(file_path, include_patterns):
        return False
    if size_limit and file_path.stat().st_size > size_limit:
        if verbose:
            logger.debug(f"🛑 Excluded by size limit: {file_path}")
        return False
    return True
