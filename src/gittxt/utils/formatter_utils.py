from pathlib import Path
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
from .subcat_utils import _detect_textual_subcat


def sort_textual_files(files: list[Path], base_path: Path = None) -> list[Path]:
    """
    Smart sort:
    1. README files first
    2. Then grouped by subcategory (docs, code, config, etc.)
    3. Then by detected language
    4. Then by relative path
    """

    def sort_key(file: Path):
        rel_path = file.relative_to(base_path) if base_path else file
        name = file.name.lower()

        # README.md first
        if name in {"readme.md", "readme"}:
            return (0, "", "", rel_path.as_posix().lower())

        subcat = _detect_textual_subcat(file)
        lang = detect_language(file)

        return (1, subcat, lang, rel_path.as_posix().lower())

    return sorted(files, key=sort_key)


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
