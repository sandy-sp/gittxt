from pathlib import Path
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

def detect_language(file: Path) -> str:
    """
    Attempts to detect programming language using Pygments based on filename.
    Returns empty string if not detected.
    """
    try:
        lexer = get_lexer_for_filename(file.name)
        return lexer.name.lower()
    except ClassNotFound:
        return ""

def sort_textual_files(files):
    """
    Simple alphabetical sort for textual files.
    """
    return sorted(files, key=lambda f: f.name.lower())
