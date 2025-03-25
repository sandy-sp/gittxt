from pathlib import Path
from typing import List, Dict
import tiktoken
from gittxt.utils.filetype_utils import classify_simple
import aiofiles

async def estimate_tokens_from_file(
    file: Path,
    encoding_name: str = "cl100k_base",
    use_fallback: bool = True
) -> int:
    """
    Estimate the number of tokens in a file.

    Args:
        file (Path): The path to the file.
        encoding_name (str): The name of the encoding to use.
        use_fallback (bool): Whether to use the fallback estimation method if tiktoken fails.

    Returns:
        int: The estimated number of tokens.
    """
    try:
        async with aiofiles.open(file, "r", encoding="utf-8", errors="ignore") as f:
            content = await f.read()
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(content)
        return len(tokens)
    except Exception:
        if use_fallback:
            try:
                async with aiofiles.open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = await f.read()
                return int(len(content.split()) * 0.75)
            except Exception:
                return 0
        return 0

def generate_summary(file_paths: List[Path], estimate_tokens: bool = True) -> Dict:
    summary = {
        "total_files": len(file_paths),
        "total_size": 0,
        "file_type_breakdown": {"binary": 0},
        "estimated_tokens": 0,
        "tokens_by_type": {},
    }

    for file in file_paths:
        if not file.exists():
            continue
        try:
            primary, sub = classify_simple(file)
            summary["total_size"] += file.stat().st_size

            # Inside file loop, ensure binary fallback:
            if sub == "blacklisted":
                sub = "binary"
            # Track file type counts
            if sub not in summary["file_type_breakdown"]:
                summary["file_type_breakdown"][sub] = 0
            summary["file_type_breakdown"][sub] += 1

            if primary == "TEXTUAL" and estimate_tokens:
                tokens = estimate_tokens_from_file(file)
                summary["estimated_tokens"] += tokens
                summary["tokens_by_type"].setdefault(sub, 0)
                summary["tokens_by_type"][sub] += tokens

        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

    return summary
