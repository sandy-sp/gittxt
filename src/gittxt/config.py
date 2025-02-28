import os
import json
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class ConfigManager:
    """Handles configuration loading and management for Gittxt."""

    # Default Configuration
    DEFAULT_CONFIG = {
        "output_dir": "gittxt-outputs",
        "size_limit": None,  # No size limit by default
        "include_patterns": [],
        "exclude_patterns": [".git", "node_modules", "__pycache__", ".log"],
        "output_format": "txt",
        "max_lines": None,
        "reuse_existing_repos": True,  # Prevent redundant cloning
        "logging_level": "INFO"  # Default logging level
    }

    # Define the config file path inside `src/gittxt/`
    SRC_DIR = os.path.dirname(__file__)  # `src/gittxt/`
    CONFIG_FILE = os.path.join(SRC_DIR, "gittxt-config.json")

    @staticmethod
    def load_config():
        """Load configuration from `gittxt-config.json`, falling back to defaults if missing or invalid."""
        if not os.path.exists(ConfigManager.CONFIG_FILE):
            logger.warning("⚠️ Config file not found. Using default settings.")
            return ConfigManager.DEFAULT_CONFIG

        try:
            with open(ConfigManager.CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            # Merge user config with defaults (user settings take priority)
            config = {**ConfigManager.DEFAULT_CONFIG, **user_config}
            logger.info("✅ Loaded configuration from gittxt-config.json.")
            return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"❌ Error loading config file: {e}. Using defaults.")
            return ConfigManager.DEFAULT_CONFIG

    @staticmethod
    def save_default_config():
        """Create a default config file if none exists."""
        if not os.path.exists(ConfigManager.CONFIG_FILE):
            with open(ConfigManager.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(ConfigManager.DEFAULT_CONFIG, f, indent=4)
            logger.info("✅ Default configuration file created: gittxt-config.json.")

# Ensure a default config exists upon import
ConfigManager.save_default_config()
