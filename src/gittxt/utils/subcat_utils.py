from pathlib import Path
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
import mimetypes

def detect_subcategory(file: Path, primary: str) -> str:
    """
    Return a sub-category string based on the top-level 'primary' category:
      - primary == 'TEXTUAL' => use Pygments to detect code/docs/config/data/etc.
      - primary == 'NON-TEXTUAL' => guess 'image', 'audio', 'pdf', 'binary', etc. via MIME or extension.
    """
    if primary == "NON-TEXTUAL":
        return _detect_non_textual_subcat(file)
    else:
        return _detect_textual_subcat(file)

def _detect_textual_subcat(file: Path) -> str:
    """
    For files classified as TEXTUAL, rely on Pygments to guess a language,
    then map that language to broad categories like code, docs, config, data, etc.
    """
    try:
        lexer = get_lexer_for_filename(file.name)
        lexer_name = lexer.name.lower()  # e.g. "python", "json", "markdown"
    except ClassNotFound:
        return "other"  # fallback if unknown or no recognized lexer

    # Simple mapping from Pygments 'lexer.name' -> subcat
    TEXTUAL_MAP = {
        "python": "code",
        "ipython console session": "code",
        "javascript": "code",
        "typescript": "code",
        "css": "code",
        "html": "code",
        "markdown": "docs",
        "json": "config",
        "yaml": "config",
        "toml": "config",
        "ini": "config",
        "csv": "data",
        "sql": "data",
    }

    # If any key in TEXTUAL_MAP is contained in the lexer_name, return that subcat
    for key, subcat in TEXTUAL_MAP.items():
        if key in lexer_name:
            return subcat

    return "other"

def _detect_non_textual_subcat(file: Path) -> str:
    """
    For files classified as NON-TEXTUAL, guess if it's image/audio/video/pdf
    or else treat it as a generic 'binary' fallback.
    """
    mime_type, _ = mimetypes.guess_type(str(file))
    if mime_type:
        mime_type = mime_type.lower()
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type == "application/pdf":
            return "pdf"
        # Add more specialized checks if you wish (e.g. docx, xls, zip, etc.)

    # If no recognized MIME => fallback
    return "binary"
