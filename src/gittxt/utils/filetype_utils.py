from pathlib import Path
import mimetypes
import json
from binaryornot.check import is_binary
from gittxt.core.config import FiletypeConfigManager

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config" / "subcategory_config.json"
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Simplified Classification: Only TEXTUAL vs NON-TEXTUAL
filetype_config = FiletypeConfigManager.load_filetype_config()
whitelist = filetype_config.get("whitelist", [])
blacklist = filetype_config.get("blacklist", [])


def is_text_file(file: Path) -> bool:
    ext = file.suffix.lower()
    if ext in blacklist:
        return False
    if ext in whitelist:
        return True

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
    ext = file.suffix.lower()

    if ext in blacklist:
        return "NON-TEXTUAL", "blacklisted"

    if ext in whitelist:
        return "TEXTUAL", "whitelisted"

    if is_text_file(file):
        return "TEXTUAL", "default"
    return "NON-TEXTUAL", "default"


def classify_file(file: Path) -> str:
    primary, _ = classify_simple(file)
    return primary


def add_to_whitelist(ext: str):
    config = FiletypeConfigManager.load_filetype_config()
    if ext in config.get("blacklist", []):
        config["blacklist"].remove(ext)
    if ext not in config.get("whitelist", []):
        config["whitelist"].append(ext)
    FiletypeConfigManager.save_filetype_config(config)


def add_to_blacklist(ext: str):
    config = FiletypeConfigManager.load_filetype_config()
    if ext in config.get("whitelist", []):
        config["whitelist"].remove(ext)
    if ext not in config.get("blacklist", []):
        config["blacklist"].append(ext)
    FiletypeConfigManager.save_filetype_config(config)
