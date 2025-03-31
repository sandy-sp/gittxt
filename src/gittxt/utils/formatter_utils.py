from pathlib import Path
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
from .subcat_utils import detect_subcategory
from gittxt.core.logger import Logger
from gittxt.utils.filetype_utils import classify_simple

logger = Logger.get_logger(__name__)


async def sort_textual_files(files: list[Path], base_path: Path = None) -> list[Path]:
    """
    Smart async sort:
    1. README files first
    2. Then grouped by subcategory (docs, code, config, etc.)
    3. Then by detected language
    4. Then by relative path
    """

    # === Step 1: Async subcategory detection ===
    subcats = {}
    for f in files:
        primary, _ = classify_simple(f)
        subcats[f] = await detect_subcategory(f, primary)

    # === Step 2: Sort with sync logic ===
    def sort_key(file: Path):
        try:
            rel_path = file.relative_to(base_path) if base_path else file
        except ValueError:
            rel_path = file.resolve()

        name = file.name.lower()
        readme_names = {"readme", "readme.md", "readme.txt", "readme.rst"}
        if name in readme_names:
            return (0, "", "", rel_path.as_posix().lower())

        subcat = subcats.get(file, "other")
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
        logger.debug(f"🔍 Language not detected for: {file.name}")
        return ""
