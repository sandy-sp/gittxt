from pathlib import Path
import mimetypes
from gittxt.core.logger import Logger
from gittxt.core.constants import DEFAULT_FILETYPE_CONFIG
from gittxt.core.config import ConfigManager

logger = Logger.get_logger(__name__)


class FiletypeConfigManager:

    @classmethod
    def load_config(cls) -> dict:
        config = ConfigManager.load_config()
        return {
            "textual_exts": config.get("textual_exts", []),
            "non_textual_exts": config.get("non_textual_exts", []),
        }

    @classmethod
    def save_config(cls, data: dict):
        ConfigManager.update_filetype_config(
            textual=data.get("textual_exts", []),
            non_textual=data.get("non_textual_exts", []),
        )

    @classmethod
    def add_textual_ext(cls, ext: str) -> bool:
        ext = ext.lower()
        if not ext.startswith("."):
            ext = f".{ext}"

        if ext in DEFAULT_FILETYPE_CONFIG["non_textual_exts"]:
            logger.warning(
                f"⚠️ Cannot add '{ext}' as textual: it's a known non-textual filetype."
            )
            return False

        config = cls.load_config()
        if ext not in config["textual_exts"]:
            if ext in config["non_textual_exts"]:
                config["non_textual_exts"].remove(ext)
            config["textual_exts"].append(ext)
            cls.save_config(config)
            return True

        return False

    @classmethod
    def add_non_textual_ext(cls, ext: str):
        config = cls.load_config()
        if ext not in config["non_textual_exts"]:
            if ext in config["textual_exts"]:
                config["textual_exts"].remove(ext)
            config["non_textual_exts"].append(ext)
        cls.save_config(config)
        logger.info(f"✅ Added '{ext}' to non_textual_exts")

    @classmethod
    def is_known_textual_ext(cls, ext: str) -> bool:
        config = cls.load_config()
        normalized = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        return normalized in config.get("textual_exts", [])


def is_binary(path: Path, chunk_size: int = 1024) -> bool:
    """
    Returns True if file appears to be binary, using null-byte scan.
    """
    try:
        with open(path, "rb") as f:
            chunk = f.read(chunk_size)
            if b"\0" in chunk:
                return True
    except Exception:
        return True  # Conservative fallback
    return False


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream"


def _is_text_file_heuristic(file: Path) -> bool:
    try:
        if is_binary(file):
            return False
        mime_type = guess_mime(file)
        if mime_type and mime_type.startswith(
            ("image/", "audio/", "video/", "application/pdf")
        ):
            return False
        return True
    except Exception as e:
        logger.debug(f"🔍 Heuristic check failed for {file.name}: {e}")
        return False


def classify_simple(file: Path) -> tuple[str, str]:
    ext = file.suffix.lower()
    config = FiletypeConfigManager.load_config()
    textual_exts = config.get("textual_exts", [])
    non_textual_exts = config.get("non_textual_exts", [])

    if ext in textual_exts:
        return ("TEXTUAL", "user_config")
    if ext in non_textual_exts:
        return ("NON-TEXTUAL", "user_config")

    if _is_text_file_heuristic(file):
        return ("TEXTUAL", "heuristic")
    return ("NON-TEXTUAL", "heuristic")


def classify_file(file: Path) -> str:
    primary, _ = classify_simple(file)
    return primary
