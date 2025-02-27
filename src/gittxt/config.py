import os
import json
from gittxt.logger import get_logger

logger = get_logger(__name__)

# Define default configuration values
DEFAULT_CONFIG = {
    "output_dir": "../gittxt-outputs",
    "size_limit": None,  # No size limit by default
    "include_patterns": [],
    "exclude_patterns": [".git", "node_modules", "__pycache__"],
    "output_format": "txt",
    "max_lines": None
}

# Config file path inside `src/gittxt/`
SRC_DIR = os.path.dirname(__file__)  # `src/gittxt/`
CONFIG_FILE = os.path.join(SRC_DIR, "gittxt-config.json")  # `src/gittxt/gittxt-config.json`

def load_config():
    """Load configuration from `gittxt-config.json`, falling back to defaults."""
    if not os.path.exists(CONFIG_FILE):
        logger.warning("Config file not found. Using default settings.")
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        
        # Merge user config with defaults (use user values if present)
        config = {**DEFAULT_CONFIG, **user_config}
        logger.info("Loaded configuration from gittxt-config.json.")
        return config
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading config file: {e}. Using defaults.")
        return DEFAULT_CONFIG
