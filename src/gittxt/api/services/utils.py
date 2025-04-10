import json
from pathlib import Path
import aiofiles

async def load_json_file(json_dir: Path) -> dict:
    if not json_dir.exists() or not json_dir.is_dir():
        raise FileNotFoundError("No summary folder found")

    files = list(json_dir.glob("*.json"))
    if not files:
        raise FileNotFoundError("No JSON summary found")

    file = files[0]
    async with aiofiles.open(file, "r", encoding="utf-8") as f:
        content = await f.read()
        return json.loads(content)
