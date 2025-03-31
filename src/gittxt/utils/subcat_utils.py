from pathlib import Path
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound
import mimetypes

from gittxt.core.logger import Logger
from gittxt.utils.file_utils import async_read_text

logger = Logger.get_logger(__name__)

async def detect_subcategory(file: Path, primary: str) -> str:
    if primary == "NON-TEXTUAL":
        return _detect_non_textual_subcat(file)
    return await _detect_textual_subcat(file)

async def _detect_textual_subcat(file: Path) -> str:
    content = await async_read_text(file)
    if not content:
        return "other"

    try:
        lexer = get_lexer_for_filename(file.name)
        lexer_name = lexer.name.lower()
    except ClassNotFound:
        lexer_name = ""

    return infer_textual_subcategory(file, content, lexer_name)

def infer_textual_subcategory(file: Path, content: str, lexer_name: str = "") -> str:
    vote = {
        "code": 0,
        "docs": 0,
        "config": 0,
        "data": 0,
        "other": 0,
    }

    name = file.name.lower()
    ext = file.suffix.lower()

    # === Language/Lexer cues ===
    if lexer_name:
        if lexer_name in {"python", "javascript", "bash", "c", "cpp", "java"}:
            vote["code"] += 2
        elif lexer_name in {"markdown", "restructuredtext"}:
            vote["docs"] += 2
        elif lexer_name in {"json", "yaml", "toml", "ini", "xml", "docker"}:
            vote["config"] += 2
        elif lexer_name in {"csv", "tsv", "sql"}:
            vote["data"] += 2

    # === Filename cues ===
    if "readme" in name or "license" in name or name.endswith(".md"):
        vote["docs"] += 1
    if "config" in name or "settings" in name:
        vote["config"] += 1
    if "data" in name:
        vote["data"] += 1

    # === Content-based keywords ===
    if any(word in content for word in ["def ", "class ", "import ", "fn ", "func "]):
        vote["code"] += 1
    if any(word in content for word in ["version:", "enabled:", "port:", "host:"]):
        vote["config"] += 1
    if any(word in content for word in [",", "id", "value", "field", "\t"]):
        vote["data"] += 1

    # === Extension fallback ===
    if ext in {".py", ".js", ".java", ".cpp", ".ts"}:
        vote["code"] += 1
    elif ext in {".md", ".rst"}:
        vote["docs"] += 1
    elif ext in {".json", ".yaml", ".yml", ".toml", ".ini"}:
        vote["config"] += 1
    elif ext in {".csv", ".tsv"}:
        vote["data"] += 1

    # Pick the subcategory with the highest vote
    subcat = max(vote, key=vote.get)
    if vote[subcat] == 0:
        return "other"
    return subcat

def _detect_non_textual_subcat(file: Path) -> str:
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