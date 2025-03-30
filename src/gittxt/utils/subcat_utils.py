from pathlib import Path
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
import mimetypes


def detect_subcategory(file: Path, primary: str) -> str:
    """
    Return a sub-category string based on the top-level 'primary' category:
      - TEXTUAL => attempt to detect 'code', 'docs', 'config', etc.
      - NON-TEXTUAL => guess 'image', 'audio', 'pdf', 'binary', etc.
    """
    if primary == "NON-TEXTUAL":
        return _detect_non_textual_subcat(file)
    return _detect_textual_subcat(file)


def _detect_textual_subcat(file: Path) -> str:
    """
    For textual files, rely on Pygments to guess a language, then map it
    to broader categories like code, docs, config, etc.
    """
    try:
        lexer = get_lexer_for_filename(file.name)
        lexer_name = lexer.name.lower()  # e.g. 'python', 'markdown'
    except ClassNotFound:
        return "other"

    TEXTUAL_MAP = {
        "python": "code",
        "ipython console session": "code",
        "javascript": "code",
        "typescript": "code",
        "html": "code",
        "markdown": "docs",
        "json": "config",
        "yaml": "config",
        "toml": "config",
        "ini": "config",
        "csv": "data",
        "sql": "data",
    }

    for key, subcat in TEXTUAL_MAP.items():
        if key in lexer_name:
            return subcat
    return "other"


def _detect_non_textual_subcat(file: Path) -> str:
    """
    For NON-TEXTUAL files, guess if it's image/audio/video/pdf
    or else treat it as a generic 'binary' fallback.
    """
    mime_type, _ = mimetypes.guess_type(str(file))
    if mime_type:
        mime_type = mime_type.lower()
        if mime_type.startswith("image/"):
            return "image"
        if mime_type.startswith("audio/"):
            return "audio"
        if mime_type.startswith("video/"):
            return "video"
        if mime_type == "application/pdf":
            return "pdf"
    return "binary"
