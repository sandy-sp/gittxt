import os
import json
from gittxt.logger import get_logger

logger = get_logger(__name__)

# Define default configuration values
DEFAULT_CONFIG = {
    "output_dir": "../gittxt-outputs",
    "size_limit": None,  # No size limit by default
    "include_patterns": [],
    "exclude_patterns": [".git", "node_modules", "__pycache__", ".vscode", "venv"],
    "output_format": "txt",
    "max_lines": None
}

# Default config file path inside `src/gittxt/`
SRC_DIR = os.path.dirname(__file__)  # `src/gittxt/`
DEFAULT_CONFIG_FILE = os.path.join(SRC_DIR, "gittxt-config.json")  # `src/gittxt/gittxt-config.json`

def load_config(config_path=None):
    """
    Load configuration from a user-specified file or fall back to `gittxt-config.json`.
    If the config file is missing or invalid, default settings are used.
    """
    config_file = config_path or DEFAULT_CONFIG_FILE  # Use provided config file or default

    if not os.path.exists(config_file):
        logger.warning(f"⚠️ Config file not found ({config_file}). Using default settings.")
        return DEFAULT_CONFIG

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        
        # Merge user config with defaults (user values override defaults)
        config = {**DEFAULT_CONFIG, **user_config}
        logger.info(f"✅ Loaded configuration from {config_file}.")
        return config
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"❌ Error loading config file {config_file}: {e}. Using defaults.")
        return DEFAULT_CONFIG
