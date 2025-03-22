from pathlib import Path
from gittxt.utils.tree_utils import generate_tree
import shutil

def build_directory_tree(path: Path, max_depth: int = None) -> str:
    """
    Wrapper around generate_tree() to produce repo tree structure.
    """
    return generate_tree(path, max_depth=max_depth)


def gather_file_extensions(path: Path) -> dict:
    """
    Recursively collect file extensions and their counts.
    """
    ext_map = {}
    for file in path.rglob("*"):
        if file.is_file():
            ext = file.suffix.lower() or "NO_EXT"
            ext_map[ext] = ext_map.get(ext, 0) + 1
    return ext_map


def remove_ephemeral_outputs(output_dir: Path):
    """
    Removes temp scan outputs (output_dir, zips, json, text, md folders).
    """
    if output_dir.exists() and output_dir.is_dir():
        shutil.rmtree(output_dir)
        print(f"🧹 Removed scan output directory: {output_dir}")
