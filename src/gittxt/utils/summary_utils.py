from pathlib import Path
from typing import List, Dict


def estimate_tokens_from_file(file_path: Path) -> int:
    """
    Estimate tokens based on word count.
    Roughly 1 token ≈ 0.75 words.
    """
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            words = f.read().split()
            return int(len(words) / 0.75)
    except Exception:
        return 0


def generate_summary(file_paths: List[Path], estimate_tokens: bool = True) -> Dict:
    """
    Generate summary for scanned files.

    :param file_paths: List of file Paths.
    :param estimate_tokens: If False, skip token estimation for speed.
    :return: Summary dict.
    """
    summary = {
        "total_files": len(file_paths),
        "total_size": 0,
        "file_types": set(),
        "estimated_tokens": 0,
    }

    for file in file_paths:
        if not file.exists():
            continue
        try:
            summary["total_size"] += file.stat().st_size
            summary["file_types"].add(file.suffix.lower())
            if estimate_tokens:
                summary["estimated_tokens"] += estimate_tokens_from_file(file)
        except Exception:
            continue

    summary["file_types"] = sorted(summary["file_types"])
    return summary
