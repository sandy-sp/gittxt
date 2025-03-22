from pathlib import Path
from gittxt.config import ConfigManager

config = ConfigManager.load_config()

def generate_tree(
    path: Path,
    prefix: str = "",
    max_depth: int = None,
    current_depth: int = 0,
    exclude_dirs: list = None,
) -> str:
    """
    Generate a directory tree structure with depth & exclude controls.

    :param path: Base path.
    :param prefix: Internal recursion prefix.
    :param max_depth: Optional max folder depth.
    :param current_depth: Tracks current recursion depth.
    :param exclude_dirs: List of folders to exclude.
    :return: Tree string.
    """
    if exclude_dirs is None:
        exclude_dirs = config.get(
            "tree_exclude_dirs",
            [".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".vscode"]
        )

    if max_depth is not None and current_depth > max_depth:
        return ""

    tree_lines = []
    try:
        contents = sorted(
            path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except Exception:
        return ""

    contents = [c for c in contents if c.name not in exclude_dirs]

    pointers = ["├── "] * (len(contents) - 1) + ["└── "] if contents else []

    for pointer, entry in zip(pointers, contents):
        tree_lines.append(f"{prefix}{pointer}{entry.name}")
        if entry.is_dir():
            extension = "│   " if pointer != "└── " else "    "
            subtree = generate_tree(
                entry, prefix + extension, max_depth, current_depth + 1, exclude_dirs
            )
            if subtree:
                tree_lines.append(subtree)

    return "\n".join(tree_lines)
