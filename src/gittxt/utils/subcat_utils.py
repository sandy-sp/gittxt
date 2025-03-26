from pathlib import Path
import mimetypes

SUBCATEGORY_CONFIG = {
    ".py": "code",
    ".js": "code",
    ".ts": "code",
    ".html": "code",
    ".css": "code",
    ".json": "config",
    ".yaml": "config",
    ".yml": "config",
    ".md": "docs",
    ".txt": "docs",
    ".csv": "data",
    ".ipynb": "notebook",
    ".test": "tests",
    ".log": "logs",
    ".pdf": "binary",
    ".zip": "binary"
}

def detect_subcategory(file: Path) -> str:
    ext = file.suffix.lower()
    if ext in SUBCATEGORY_CONFIG:
        return SUBCATEGORY_CONFIG[ext]

    mime, _ = mimetypes.guess_type(str(file))
    if mime:
        if mime.startswith("image/"):
            return "image"
        elif mime.startswith("audio/") or mime.startswith("video/"):
            return "media"
        elif mime.startswith("application/pdf"):
            return "binary"

    return "other"
