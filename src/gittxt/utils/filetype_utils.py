from pathlib import Path
import mimetypes
from binaryornot.check import is_binary
from gittxt.core.logger import Logger
import json

logger = Logger.get_logger(__name__)

# Updated config keys to textual_exts / non_textual_exts instead of whitelist/blacklist
DEFAULT_FILETYPE_CONFIG = {
    "textual_exts": [".py", ".md", ".txt", ".html", ".json", ".yml", ".yaml", ".csv"],
    "non_textual_exts": [".zip", ".exe", ".bin", ".docx", ".xls", ".pdf"],
}

class FiletypeConfigManager:
    """
    Manages textual_exts and non_textual_exts in a config file (was formerly whitelist/blacklist).
    """
    CONFIG_FILE = Path(__file__).parent.parent / "config" / "filetype_config.json"

    @classmethod
    def load_config(cls) -> dict:
        if cls.CONFIG_FILE.exists():
            try:
                with cls.CONFIG_FILE.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Could not load filetype config: {e}. Using defaults.")
                return DEFAULT_FILETYPE_CONFIG.copy()
        else:
            return DEFAULT_FILETYPE_CONFIG.copy()

    @classmethod
    def save_config(cls, data: dict):
        try:
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with cls.CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Failed to update filetype config: {e}")

    @classmethod
    def add_textual_ext(cls, ext: str):
        config = cls.load_config()
        if ext not in config["textual_exts"]:
            # remove from non_textual if needed
            if ext in config["non_textual_exts"]:
                config["non_textual_exts"].remove(ext)
            config["textual_exts"].append(ext)
        cls.save_config(config)

    @classmethod
    def add_non_textual_ext(cls, ext: str):
        config = cls.load_config()
        if ext not in config["non_textual_exts"]:
            # remove from textual if needed
            if ext in config["textual_exts"]:
                config["textual_exts"].remove(ext)
            config["non_textual_exts"].append(ext)
        cls.save_config(config)


def _is_text_file_heuristic(file: Path) -> bool:
    """
    Basic textual check using binaryornot and MIME type.
    """
    try:
        if is_binary(str(file)):
            return False
        mime_type, _ = mimetypes.guess_type(str(file))
        if mime_type and mime_type.startswith(("image/", "audio/", "video/")):
            return False
        return True
    except Exception:
        return False

def classify_simple(file: Path) -> tuple[str, str]:
    """
    Returns ("TEXTUAL" or "NON-TEXTUAL", reason).
    Reason: "user_config" if matched by config, or "heuristic" otherwise.
    """
    ext = file.suffix.lower()
    config = FiletypeConfigManager.load_config()
    textual_exts = config.get("textual_exts", [])
    non_textual_exts = config.get("non_textual_exts", [])

    if ext in textual_exts:
        return ("TEXTUAL", "user_config")
    if ext in non_textual_exts:
        return ("NON-TEXTUAL", "user_config")

    # Fallback to heuristic
    if _is_text_file_heuristic(file):
        return ("TEXTUAL", "heuristic")
    return ("NON-TEXTUAL", "heuristic")

def classify_file(file: Path) -> str:
    """
    Returns 'TEXTUAL' or 'NON-TEXTUAL' only, skipping the reason.
    """
    primary, _reason = classify_simple(file)
    return primary
