import os
import json
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class ConfigManager:
    """Handles configuration loading and management for Gittxt."""

    # Default Configuration
    DEFAULT_CONFIG = {
        "output_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs")),
        "size_limit": None,  # No size limit by default
        "include_patterns": [],
        "exclude_patterns": [".git", "node_modules", "__pycache__", ".log"],
        "output_format": "txt",
        "max_lines": None,
        "reuse_existing_repos": True,  # Prevent redundant cloning
        "logging_level": "INFO"  # Default logging level
    }

    # Define the absolute path for the config file inside `src/gittxt/`
    SRC_DIR = os.path.dirname(__file__)
    CONFIG_FILE = os.path.join(SRC_DIR, "gittxt-config.json")

    @classmethod
    def load_config(cls):
        """Load configuration from `gittxt-config.json`, falling back to defaults if missing or invalid."""
        if not os.path.exists(cls.CONFIG_FILE):
            logger.warning("⚠️ Config file not found. Using default settings.")
            return cls.DEFAULT_CONFIG

        try:
            with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            # Merge user config with defaults (user settings take priority)
            config = {**cls.DEFAULT_CONFIG, **user_config}

            # Ensure `output_dir` is always absolute
            config["output_dir"] = os.path.abspath(config["output_dir"])

            logger.info(f"✅ Loaded configuration from {cls.CONFIG_FILE}")
            return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"❌ Error loading config file: {e}. Using defaults.")
            return cls.DEFAULT_CONFIG

    @classmethod
    def save_default_config(cls):
        """Create a default config file if none exists."""
        if not os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cls.DEFAULT_CONFIG, f, indent=4)
            logger.info(f"✅ Default configuration file created: {cls.CONFIG_FILE}")

# Ensure a default config exists upon import
ConfigManager.save_default_config()
