from pathlib import Path

def generate_tree(path: Path, prefix: str = "") -> str:
    """
    Generate a directory tree string similar to the 'tree' command.

    :param path: The base path to generate the tree from.
    :param prefix: Used internally for formatting recursion.
    :return: Tree string.
    """
    tree_lines = []
    contents = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    pointers = ["├── "] * (len(contents) - 1) + ["└── "] if contents else []

    for pointer, entry in zip(pointers, contents):
        tree_lines.append(f"{prefix}{pointer}{entry.name}")
        if entry.is_dir():
            extension = "│   " if pointer != "└── " else "    "
            subtree = generate_tree(entry, prefix=prefix + extension)
            if subtree:
                tree_lines.append(subtree)
    
    return "\n".join(tree_lines)
