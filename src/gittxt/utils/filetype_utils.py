from pathlib import Path
import mimetypes
from binaryornot.check import is_binary
from gittxt.config import FiletypeConfigManager

# Centralized config access
FILETYPE_CONFIG = FiletypeConfigManager.load_filetype_config()


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

        # Basic density checks
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
    return file.suffix.lower() in FILETYPE_CONFIG.get("whitelist", [])


def is_blacklisted(file: Path) -> bool:
    return file.suffix.lower() in FILETYPE_CONFIG.get("blacklist", [])


def pipeline_classify(file: Path) -> str:
    """
    Multi-stage pipeline:
    1) Whitelist always wins
    2) Blacklist always rejects
    3) Extension rules
    4) MIME fallback
    5) Content sampling heuristic fallback
    """
    suffix = file.suffix.lower()

    # 🥇 Whitelist override
    if is_whitelisted(file):
        return "text"

    # 🥈 Blacklist override
    if is_blacklisted(file):
        return "asset"

    # 🥉 Common static rules
    static_text_exts = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".cs", ".go", ".rb",
        ".php", ".sh", ".md", ".rst", ".txt", ".csv", ".json", ".yaml", ".yml", ".xml",
        ".html", ".toml", ".ini"
    }
    if suffix in static_text_exts:
        return "text"

    # MIME fallback (e.g., text/plain, text/html)
    mime_type = get_mime_type(file)
    if mime_type.startswith("text/") or mime_type in {"application/json", "application/xml"}:
        return "text"

    # Content sampling fallback
    if is_text_file(file) and looks_like_text_content(file):
        return "text"

    return "asset"


def classify_file(file: Path) -> str:
    return pipeline_classify(file)


def update_whitelist(ext: str):
    """Proxy to centralized config manager."""
    FiletypeConfigManager.add_to_whitelist(ext)


def update_blacklist(ext: str):
    """Proxy to centralized config manager."""
    FiletypeConfigManager.add_to_blacklist(ext)
