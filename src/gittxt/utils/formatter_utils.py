from pathlib import Path
from gittxt.utils.filetype_utils import classify_simple

def sort_textual_files(files):
    """
    Simple alphabetical sort for textual files.
    You can enhance later with custom sort by size, name, etc.
    """
    return sorted(files, key=lambda f: f.name.lower())
