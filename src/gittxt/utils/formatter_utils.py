from pathlib import Path
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
from .subcat_utils import infer_textual_subcategory
from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)

async def sort_textual_files(files: list[Path], base_path: Path = None) -> list[Path]:
    """
    Smart async sort:
    1. README files first
    2. Then grouped by subcategory
    3. Then by detected language
    4. Then by relative path
    """
    subcats = {}
    for f in files:
        subcats[f] = await infer_textual_subcategory(f)

    def sort_key(file: Path):
        name = file.name.lower()
        if name in {"readme", "readme.md", "readme.txt", "readme.rst"}:
            return (0, "", "", file.as_posix().lower())

        subcat = subcats.get(file, "other")
        lang = detect_language(file)
        try:
            rel_path = file.relative_to(base_path) if base_path else file
        except ValueError:
            rel_path = file.resolve()

        return (1, subcat, lang, rel_path.as_posix().lower())

    return sorted(files, key=sort_key)

def detect_language(file: Path) -> str:
    try:
        lexer = get_lexer_for_filename(file.name)
        return lexer.name.lower()
    except ClassNotFound:
        logger.debug(f"🔍 Language not detected for: {file.name}")
        return ""
