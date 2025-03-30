from pathlib import Path
from typing import List, Dict
import aiofiles
import humanize
import tiktoken
from gittxt.utils.filetype_utils import classify_simple
from gittxt.utils.subcat_utils import detect_subcategory


def format_number_short(n: int) -> str:
    """
    Return a short string for large numbers:
      - 1,234 => '1.2k'
      - 1,000,000 => '1.0M'
    """
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def format_size_short(n: int) -> str:
    """
    Use humanize.naturalsize to produce a more readable size,
    e.g., 1024 => '1.0 kB'.
    """
    return humanize.naturalsize(n, binary=False)


async def estimate_tokens_from_file(
    file: Path, encoding_name: str = "cl100k_base", use_fallback: bool = True
) -> int:
    """
    Estimate the number of tokens by reading the file and using tiktoken.
    Fallback is length/4 if tiktoken fails or not installed.
    """
    try:
        async with aiofiles.open(file, "r", encoding="utf-8", errors="ignore") as f:
            content = await f.read()
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(content))
        except Exception:
            return int(len(content) / 4) if use_fallback else 0
    except Exception:
        return 0


async def generate_summary(
    file_paths: List[Path], estimate_tokens: bool = True
) -> Dict:
    """
    Return a summary dict with:
      - total_files
      - total_size (raw bytes)
      - file_type_breakdown
      - estimated_tokens (raw int)
      - tokens_by_type (raw ints per subcat)
      - formatted (human-readable versions for display)
    """
    summary = {
        "total_files": len(file_paths),
        "total_size": 0,
        "file_type_breakdown": {},
        "estimated_tokens": 0,
        "tokens_by_type": {},
    }

    for file in file_paths:
        if not file.exists():
            continue
        primary, _reason = classify_simple(file)
        subcat = detect_subcategory(file, primary)
        size = file.stat().st_size
        summary["total_size"] += size

        summary["file_type_breakdown"].setdefault(subcat, 0)
        summary["file_type_breakdown"][subcat] += 1

        if primary == "TEXTUAL" and estimate_tokens:
            tokens = await estimate_tokens_from_file(file)
            summary["estimated_tokens"] += tokens
            summary["tokens_by_type"].setdefault(subcat, 0)
            summary["tokens_by_type"][subcat] += tokens

    # Add human-readable formatting (does not affect downstream logic)
    summary["formatted"] = {
        "total_size": format_size_short(summary.get("total_size", 0)),
        "estimated_tokens": format_number_short(summary.get("estimated_tokens", 0)),
        "tokens_by_type": {
            subcat: format_number_short(tokens)
            for subcat, tokens in summary.get("tokens_by_type", {}).items()
        },
    }

    return summary
