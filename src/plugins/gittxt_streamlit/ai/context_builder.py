from pathlib import Path
import os

MAX_TOKENS = 8000
SUPPORTED_EXTS = {".md", ".txt", ".json"}


def build_context(files, include_txt=False, include_json=False, full_mode=False):
    """
    Builds a concatenated string context from given files with optional token truncation.

    Args:
        files (list): List of file paths (str or Path).
        include_txt (bool): Whether to include .txt files.
        include_json (bool): Whether to include .json files.
        full_mode (bool): If True, do not truncate based on token count.

    Returns:
        context_text (str): Combined file content.
        used_files (list): List of filenames included.
        token_estimate (int): Crude token estimate.
    """
    context_parts = []
    token_estimate = 0
    used_files = []

    allowed_exts = {".md"}
    if include_txt:
        allowed_exts.add(".txt")
    if include_json:
        allowed_exts.add(".json")

    for f in files:
        ext = Path(f).suffix.lower()
        if ext not in allowed_exts:
            continue
        try:
            text = Path(f).read_text(encoding="utf-8")
        except Exception:
            continue

        tokens = len(text.split())
        if not full_mode and (token_estimate + tokens > MAX_TOKENS):
            break

        context_parts.append(f"\n\n### {Path(f).name}\n\n{text}")
        used_files.append(Path(f).name)
        token_estimate += tokens

    return "\n".join(context_parts), used_files, token_estimate
