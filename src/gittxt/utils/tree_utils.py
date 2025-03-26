from pathlib import Path
import os

def generate_tree(path: Path, prefix: str = "", max_depth: int = None, current_depth: int = 0, exclude_dirs: list = None) -> str:
    """
    Generate a directory tree structure with optional max depth & excludes.
    """
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".vscode"]

    if max_depth is not None and current_depth >= max_depth:
        return prefix.rstrip() + "└── ..."

    lines = []
    try:
        with os.scandir(path) as entries:
            entries_list = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
            # Filter out excluded directories
            entries_list = [e for e in entries_list if e.name not in exclude_dirs]

            pointers = ["├── "] * (len(entries_list) - 1) + ["└── "] if entries_list else []
            for pointer, entry in zip(pointers, entries_list):
                lines.append(f"{prefix}{pointer}{entry.name}")
                if entry.is_dir():
                    extension = "│   " if pointer != "└── " else "    "
                    subtree = generate_tree(Path(entry.path), prefix + extension, max_depth, current_depth + 1, exclude_dirs)
                    if subtree:
                        lines.append(subtree)
    except Exception:
        return ""

    return "\n".join(lines)
