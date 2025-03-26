# src/gittxt/utils/summary_utils.py

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
    file: Path,
    encoding_name: str = "cl100k_base",
    use_fallback: bool = True
) -> int:
    """
    Estimate the number of tokens in a file using tiktoken.
    Falls back to a naive 'len(content)//4' if tiktoken fails or is missing.
    """
    try:
        async with aiofiles.open(file, "r", encoding="utf-8", errors="ignore") as f:
            content = await f.read()
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(content))
        except Exception:
            if use_fallback:
                return int(len(content) / 4)
            return 0
    except Exception:
        return 0

async def generate_summary(file_paths: List[Path], estimate_tokens: bool = True) -> Dict:
    """
    Produce a summary dict with:
      - total_files
      - total_size
      - file_type_breakdown (sub-cat => count)
      - estimated_tokens
      - tokens_by_type (sub-cat => token sum)

    Classification steps:
      1. classify_simple(file) => TEXTUAL or NON-TEXTUAL
      2. detect_subcategory(file, primary) => code, docs, config, image, audio, binary, etc.
    """
    summary = {
        "total_files": len(file_paths),
        "total_size": 0,
        "file_type_breakdown": {},     # e.g. {"code": 12, "docs": 5, "binary": 2, ...}
        "estimated_tokens": 0,
        "tokens_by_type": {},         # e.g. {"code": 10000, "docs": 3000, ...}
    }

    for file in file_paths:
        if not file.exists():
            continue

        try:
            # Step 1: TEXTUAL or NON-TEXTUAL
            primary, _reason = classify_simple(file)  # e.g. (TEXTUAL, 'whitelisted') or (NON-TEXTUAL, 'blacklisted')

            # Step 2: Sub-category detection
            subcat = detect_subcategory(file, primary)  # e.g. 'code', 'docs', 'image', 'binary', etc.

            # Accumulate size
            file_size = file.stat().st_size
            summary["total_size"] += file_size

            # Bump sub-cat count
            if subcat not in summary["file_type_breakdown"]:
                summary["file_type_breakdown"][subcat] = 0
            summary["file_type_breakdown"][subcat] += 1

            # If textual => optionally estimate tokens
            if primary == "TEXTUAL" and estimate_tokens:
                tokens = await estimate_tokens_from_file(file)
                summary["estimated_tokens"] += tokens
                if subcat not in summary["tokens_by_type"]:
                    summary["tokens_by_type"][subcat] = 0
                summary["tokens_by_type"][subcat] += tokens

        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

    return summary
