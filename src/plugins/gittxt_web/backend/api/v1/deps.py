from pathlib import Path
from gittxt.core.config import ConfigManager

def get_output_dir() -> Path:
    config = ConfigManager.load_config()
    return Path(config.get("output_dir", "./gittxt_output")).resolve()
