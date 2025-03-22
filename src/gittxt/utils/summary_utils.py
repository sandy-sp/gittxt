from pathlib import Path
from typing import List, Dict
import tiktoken
from gittxt.utils.filetype_utils import classify_simple

def estimate_tokens_from_file(file: Path, encoding_name: str = "cl100k_base") -> int:
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
    summary = {
        "total_files": len(file_paths),
        "total_size": 0,
        "TEXTUAL": {
            "code": 0,
            "docs": 0,
            "configs": 0,
            "data": 0,
            "estimated_tokens": 0,
            "tokens_by_type": {
                "code": 0,
                "docs": 0,
                "configs": 0,
                "data": 0
            }
        },
        "NON-TEXTUAL": {
            "image": 0,
            "media": 0,
            "binary": 0
        }
    }

    for file in file_paths:
        if not file.exists():
            continue
        try:
            primary, sub = classify_simple(file)
            summary["total_size"] += file.stat().st_size

            if primary == "TEXTUAL":
                summary["TEXTUAL"][sub] += 1
                if estimate_tokens:
                    tokens = estimate_tokens_from_file(file)
                    summary["TEXTUAL"]["estimated_tokens"] += tokens
                    summary["TEXTUAL"]["tokens_by_type"][sub] += tokens

            elif primary == "NON-TEXTUAL":
                summary["NON-TEXTUAL"][sub] += 1

        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

    return summary
