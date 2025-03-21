from pathlib import Path
from typing import List, Dict
import tiktoken
from gittxt.utils.filetype_utils import classify_file

def estimate_tokens_from_file(file: Path, encoding_name: str = "cl100k_base") -> int:
    """
    Estimate the number of tokens in a text file using tiktoken.

    Args:
        file (Path): Path to the text file.
        encoding_name (str): The encoding to use for tokenization.

    Returns:
        int: Estimated number of tokens.
    """
    try:
        with file.open("r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(content)
        return len(tokens)
    except Exception as e:
        print(f"Error processing {file}: {e}")
        return 0

def generate_summary(file_paths: List[Path], estimate_tokens: bool = True) -> Dict:
    """
    Generate a summary of the provided files, including total size, file type breakdown,
    and estimated token count.

    Args:
        file_paths (List[Path]): List of file paths to include in the summary.
        estimate_tokens (bool): Whether to estimate token counts for text files.

    Returns:
        Dict: Summary statistics.
    """
    summary = {
        "total_files": len(file_paths),
        "total_size": 0,
        "file_type_breakdown": {
            "code": 0,
            "docs": 0,
            "csv": 0,
            "image": 0,
            "media": 0,
            "asset": 0
        },
        "estimated_tokens": 0,
        "tokens_by_type": {
            "code": 0,
            "docs": 0,
            "csv": 0
        }
    }

    for file in file_paths:
        if not file.exists():
            continue
        try:
            classification = classify_file(file)
            summary["total_size"] += file.stat().st_size

            if classification in summary["file_type_breakdown"]:
                summary["file_type_breakdown"][classification] += 1
            else:
                summary["file_type_breakdown"]["asset"] += 1  # fallback bucket

            if classification in {"code", "docs", "csv"} and estimate_tokens:
                tokens = estimate_tokens_from_file(file)
                summary["estimated_tokens"] += tokens
                summary["tokens_by_type"][classification] += tokens

        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

    return summary
