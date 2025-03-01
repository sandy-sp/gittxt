import os
import json
import platform
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class ConfigManager:
    """Handles configuration loading and management for Gittxt."""

    SRC_DIR = os.path.dirname(__file__)
    CONFIG_FILE = os.path.join(SRC_DIR, "gittxt-config.json")

    @staticmethod
    def _determine_default_output_dir():
        """
        Choose a user-accessible default directory based on the OS.
        - Windows: ~/Documents/Gittxt
        - Mac: ~/Documents/Gittxt
        - Linux/Other: ~/Gittxt
        """
        system_name = platform.system().lower()
        home_dir = os.path.expanduser("~")

        if system_name.startswith("win"):
            # Windows
            return os.path.abspath(os.path.join(home_dir, "Documents", "Gittxt"))
        elif system_name.startswith("darwin"):
            # macOS
            return os.path.abspath(os.path.join(home_dir, "Documents", "Gittxt"))
        else:
            # Linux / Other Unix
            return os.path.abspath(os.path.join(home_dir, "Gittxt"))

    # Default Configuration
    DEFAULT_CONFIG = {
        "output_dir": _determine_default_output_dir.__func__(),  # Evaluate method at import
        "size_limit": None,  # No size limit by default
        "include_patterns": [],
        "exclude_patterns": [".git", "node_modules", "__pycache__", ".log"],
        "output_format": "txt",
        "max_lines": None,
        "reuse_existing_repos": True,  # Prevent redundant cloning
        "logging_level": "INFO"        # Default logging level
    }

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

    @classmethod
    def save_config_updates(cls, updated_config: dict):
        """
        Overwrite gittxt-config.json with the updated config dictionary.
        Useful for 'gittxt install' or other dynamic config changes.
        """
        try:
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(updated_config, f, indent=4)
            logger.info(f"✅ Configuration updated in {cls.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"❌ Failed to update configuration file: {e}")

# Ensure a default config exists upon import
ConfigManager.save_default_config()
