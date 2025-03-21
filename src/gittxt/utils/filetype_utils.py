from pathlib import Path
import mimetypes
import time
from binaryornot.check import is_binary
from gittxt.config import FiletypeConfigManager

# Cache TTL in seconds (e.g., refresh every 60 seconds)
CACHE_TTL = 60

class ConfigCache:
    """Simple TTL-based config cache."""
    def __init__(self):
        self.last_loaded = 0
        self.config = {}

    def load(self):
        now = time.time()
        if now - self.last_loaded > CACHE_TTL:
            self.config = FiletypeConfigManager.load_filetype_config()
            self.last_loaded = now
        return self.config


config_cache = ConfigCache()


def is_text_file(file: Path) -> bool:
    """Check if file is not binary based on content."""
    try:
        if file.is_dir() or not file.exists() or not file.is_file():
            return False
        return not is_binary(str(file))
    except Exception:
        return False


def get_mime_type(file: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(file))
    return mime_type or "application/octet-stream"


def looks_like_text_content(file: Path) -> bool:
    """Heuristic: open file and inspect first 2 KB"""
    try:
        with file.open("rb") as f:
            sample = f.read(2048)
        decoded = sample.decode("utf-8", errors="ignore")

        alpha_ratio = sum(c.isalpha() for c in decoded) / (len(decoded) + 1)
        keyword_hits = sum(
            1 for kw in ["function", "class", "def", "import", "module", "{", "}", "<", ">"]
            if kw in decoded.lower()
        )
        if alpha_ratio > 0.25 or keyword_hits >= 1:
            return True
    except Exception:
        pass
    return False


def is_whitelisted(file: Path) -> bool:
    config = config_cache.load()
    return file.suffix.lower() in config.get("whitelist", [])


def is_blacklisted(file: Path) -> bool:
    config = config_cache.load()
    return file.suffix.lower() in config.get("blacklist", [])


def pipeline_classify(file: Path) -> str:
    """
    Multi-stage pipeline:
    1) Whitelist always wins
    2) Blacklist always rejects
    3) Static extension rules
    4) MIME fallback
    5) Content sampling fallback
    """
    suffix = file.suffix.lower()
    mime_type = get_mime_type(file)

    # Whitelist override
    if is_whitelisted(file):
        return classify_text_type(file)

    # Blacklist override
    if is_blacklisted(file):
        return "asset"

    # Static extension heuristic
    static_text_exts = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".cs", ".go", ".rb",
        ".php", ".sh", ".md", ".rst", ".txt", ".csv", ".json", ".yaml", ".yml", ".xml",
        ".html", ".toml", ".ini", ".env", ".cfg", ".dockerfile", ".ipynb"
    }

    static_image_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"}
    static_media_exts = {".mp4", ".mp3", ".wav", ".avi", ".mov", ".flac", ".mkv"}

    if suffix in static_text_exts:
        return classify_text_type(file)
    elif suffix in static_image_exts:
        return "image"
    elif suffix in static_media_exts:
        return "media"

    # MIME fallback
    MIME_TYPE_MAP = {
        "application/javascript": "code",
        "application/json": "docs",
        "application/xml": "docs",
        "text/x-python": "code",
        "text/html": "docs",
        "text/markdown": "docs",
        "text/csv": "csv",
    }

    if mime_type in MIME_TYPE_MAP:
        return MIME_TYPE_MAP[mime_type]
    if mime_type.startswith("text/") or mime_type in {"application/json", "application/xml"}:
        return classify_text_type(file)
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("audio/") or mime_type.startswith("video/"):
        return "media"

    # Content sampling fallback
    if is_text_file(file) and looks_like_text_content(file):
        return classify_text_type(file)

    return "asset"


def classify_text_type(file: Path) -> str:
    """Secondary classification for text-like files."""
    ext = file.suffix.lower()
    if ext in {".py", ".js", ".ts", ".cpp", ".c", ".go", ".rb", ".php", ".sh"}:
        return "code"
    if ext in {".md", ".rst", ".txt", ".html"}:
        return "docs"
    if ext in {".csv"}:
        return "csv"
    if ext in {".json", ".yaml", ".yml", ".xml", ".toml", ".ini"}:
        return "docs"
    if ext in {".ipynb"}:
        return "code"
    return "docs"  # fallback


def classify_file(file: Path) -> str:
    return pipeline_classify(file)


def update_whitelist(ext: str):
    FiletypeConfigManager.add_to_whitelist(ext)
    config_cache.last_loaded = 0  # Force reload next time


def update_blacklist(ext: str):
    FiletypeConfigManager.add_to_blacklist(ext)
    config_cache.last_loaded = 0  # Force reload next time
