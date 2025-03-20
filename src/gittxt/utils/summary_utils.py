from pathlib import Path
from typing import List, Dict
from gittxt.utils.filetype_utils import classify_file

def estimate_tokens_from_file(file_path: Path) -> int:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            words = f.read().split()
            return int(len(words) / 0.75)
    except Exception:
        return 0

def generate_summary(file_paths: List[Path], estimate_tokens: bool = True) -> Dict:
    summary = {
        "total_files": len(file_paths),
        "total_size": 0,
        "text_files": 0,
        "asset_files": 0,
        "estimated_tokens": 0,
    }

    for file in file_paths:
        if not file.exists():
            continue
        try:
            classification = classify_file(file)
            summary["total_size"] += file.stat().st_size

            if classification == "text":
                summary["text_files"] += 1
                if estimate_tokens:
                    summary["estimated_tokens"] += estimate_tokens_from_file(file)
            else:
                summary["asset_files"] += 1
        except Exception:
            continue

    return summary
