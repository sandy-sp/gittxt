from pathlib import Path
from typing import List
import fnmatch

def match_include(file_path: Path, include_patterns: List[str]) -> bool:
    """
    Check if the file matches any of the include patterns (e.g., ".py", ".md").

    :param file_path: Path to file.
    :param include_patterns: List of strings like [".py", ".md"].
    :return: True if file matches includes, or if include_patterns is empty (default allow).
    """
    if not include_patterns:
        return True  # Default to include all if no patterns
    return any(fnmatch.fnmatch(str(file_path), pattern) for pattern in include_patterns)


def match_exclude(file_path: Path, exclude_patterns: List[str]) -> bool:
    """
    Check if the file should be excluded based on folder or extension.

    :param file_path: Path to file.
    :param exclude_patterns: List of patterns like ["node_modules", ".git"].
    :return: True if file matches any exclusion pattern.
    """
    return any(fnmatch.fnmatch(str(file_path), pattern) for pattern in exclude_patterns)


def normalize_patterns(patterns: List[str]) -> List[str]:
    """
    Normalize patterns to lower-case and strip whitespace.

    :param patterns: Raw pattern list.
    :return: Clean list of patterns.
    """
    return [p.strip().lower() for p in patterns if p.strip()]
