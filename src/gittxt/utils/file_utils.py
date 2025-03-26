from pathlib import Path
import aiofiles
from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)

async def async_read_text(file_path: Path) -> str:
    """
    Asynchronously read a file as text (UTF-8, ignoring errors).
    """
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return await f.read()
    except Exception as e:
        logger.warning(f"⚠️ Failed to read file {file_path}: {e}")
        return None

def load_gittxtignore(repo_path: Path) -> list:
    """
    Load .gittxtignore patterns from a repository root, returning them as a list.
    """
    ignore_file = repo_path / ".gittxtignore"
    if ignore_file.exists():
        patterns = ignore_file.read_text(encoding="utf-8").splitlines()
        return [p.strip() for p in patterns if p.strip() and not p.startswith("#")]
    return []
