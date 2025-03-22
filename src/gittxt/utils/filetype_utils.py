from pathlib import Path
import mimetypes
import json
from binaryornot.check import is_binary
from gittxt.config import FiletypeConfigManager

CONFIG_FILE = Path(__file__).parent / "../subcategory_config.json"

# --- Dynamic Configurable Subcategory Map ---

DEFAULT_SUBCATEGORY_MAP = {
    "TEXTUAL": {
        "code": [".py", ".js", ".ts", ".cpp", ".c", ".go", ".java", ".rb", ".php", ".sh"],
        "docs": [".md", ".txt", ".rst", ".html", ".htm", "readme", "license", "notice"],
        "configs": [".yml", ".yaml", ".ini", ".toml", ".cfg", ".env", ".in", "dockerfile", "makefile"],
        "data": [".csv", ".json"]
    },
    "NON-TEXTUAL": {
        "image": [".png", ".jpg", ".jpeg", ".svg", ".webp"],
        "media": [".mp4", ".mp3", ".wav", ".avi", ".mkv"],
        "binary": [".zip", ".exe", ".dll", ".bin", ".so"]
    }
}

# Load or create config
if CONFIG_FILE.exists():
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        SUBCATEGORY_MAP = json.load(f)
else:
    SUBCATEGORY_MAP = DEFAULT_SUBCATEGORY_MAP.copy()
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(SUBCATEGORY_MAP, f, indent=4)

# Load filetype_config.json whitelist/blacklist
filetype_config = FiletypeConfigManager.load_filetype_config()
whitelist = filetype_config.get("whitelist", [])
blacklist = filetype_config.get("blacklist", [])


def is_text_file(file: Path) -> bool:
    try:
        if file.is_dir() or not file.exists() or not file.is_file():
            return False
        return not is_binary(str(file))
    except Exception:
        return False


def classify_simple(file: Path) -> tuple[str, str]:
    ext = file.suffix.lower()
    fname = file.name.lower()

    if ext in blacklist:
        return "NON-TEXTUAL", "blacklisted"

    if ext in whitelist:
        return "TEXTUAL", "custom"

    if is_text_file(file):
        for subcat, patterns in SUBCATEGORY_MAP["TEXTUAL"].items():
            if ext in patterns or fname in patterns:
                return "TEXTUAL", subcat
        return "TEXTUAL", "docs"  # fallback

    else:
        for subcat, patterns in SUBCATEGORY_MAP["NON-TEXTUAL"].items():
            if ext in patterns or fname in patterns:
                return "NON-TEXTUAL", subcat
        mime_type, _ = mimetypes.guess_type(str(file))
        if mime_type and mime_type.startswith("image/"):
            return "NON-TEXTUAL", "image"
        if mime_type and (mime_type.startswith("audio/") or mime_type.startswith("video/")):
            return "NON-TEXTUAL", "media"
        return "NON-TEXTUAL", "binary"  # fallback


def classify_file(file: Path) -> str:
    """Returns simplified label for CLI/API e.g., code, docs, image, etc."""
    _, subcat = classify_simple(file)
    return subcat


def add_to_subcategory(category: str, subcategory: str, ext_or_name: str):
    global SUBCATEGORY_MAP
    if category not in SUBCATEGORY_MAP:
        SUBCATEGORY_MAP[category] = {}
    if subcategory not in SUBCATEGORY_MAP[category]:
        SUBCATEGORY_MAP[category][subcategory] = []
    SUBCATEGORY_MAP[category][subcategory].append(ext_or_name)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(SUBCATEGORY_MAP, f, indent=4)


def move_extension(ext_or_name: str, from_sub: tuple[str, str], to_sub: tuple[str, str]):
    global SUBCATEGORY_MAP
    # remove from old
    SUBCATEGORY_MAP[from_sub[0]][from_sub[1]].remove(ext_or_name)
    # add to new
    add_to_subcategory(to_sub[0], to_sub[1], ext_or_name)
