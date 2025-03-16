from pathlib import Path

def generate_tree(path: Path, prefix: str = "", max_depth: int = None, current_depth: int = 0) -> str:
    """
    Generate a directory tree structure, optionally with depth control.

    :param path: Base path.
    :param prefix: Used internally for recursion.
    :param max_depth: Optional max depth for folders.
    :param current_depth: Tracks current recursion depth.
    :return: Tree string.
    """
    if max_depth is not None and current_depth > max_depth:
        return ""

    tree_lines = []
    try:
        contents = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except Exception:
        return ""

    pointers = ["├── "] * (len(contents) - 1) + ["└── "] if contents else []

    for pointer, entry in zip(pointers, contents):
        tree_lines.append(f"{prefix}{pointer}{entry.name}")
        if entry.is_dir():
            extension = "│   " if pointer != "└── " else "    "
            subtree = generate_tree(entry, prefix + extension, max_depth, current_depth + 1)
            if subtree:
                tree_lines.append(subtree)

    return "\n".join(tree_lines)
