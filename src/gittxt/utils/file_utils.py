from pathlib import Path
import aiofiles

async def async_read_text(file_path: Path) -> str:
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return await f.read()
    except Exception:
        return None
