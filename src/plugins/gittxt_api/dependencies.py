from pathlib import Path
from gittxt.core.config import ConfigManager

config = ConfigManager.load_config()
OUTPUT_DIR = Path(config.get("output_dir", "./gittxt_output")).resolve()
