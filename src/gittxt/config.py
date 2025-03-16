from pathlib import Path
import json
import platform
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class ConfigManager:
    """Handles configuration loading and management for Gittxt."""

    SRC_DIR = Path(__file__).parent.resolve()
    CONFIG_FILE = SRC_DIR / "gittxt-config.json"

    @staticmethod
    def _determine_default_output_dir():
        """
        Choose a user-accessible default directory based on the OS.
        - Windows: ~/Documents/Gittxt
        - Mac: ~/Documents/Gittxt
        - Linux/Other: ~/Gittxt
        """
        system_name = platform.system().lower()
        home_dir = Path.home()

        if system_name.startswith("win") or system_name.startswith("darwin"):
            return (home_dir / "Documents" / "Gittxt").resolve()
        else:
            return (home_dir / "Gittxt").resolve()

    DEFAULT_CONFIG = {
        "output_dir": str(_determine_default_output_dir.__func__()),  # evaluated at import
        "size_limit": None,
        "include_patterns": [],
        "exclude_patterns": [".git", "node_modules", "__pycache__", ".log"],
        "output_format": "txt",
        "max_lines": None,
        "reuse_existing_repos": True,
        "logging_level": "INFO"
    }

    @classmethod
    def load_config(cls):
        """Load configuration from gittxt-config.json, fallback to defaults if missing or invalid."""
        if not cls.CONFIG_FILE.exists():
            logger.warning("⚠️ Config file not found. Using default settings.")
            return cls.DEFAULT_CONFIG

        try:
            with cls.CONFIG_FILE.open("r", encoding="utf-8") as f:
                user_config = json.load(f)

            config = {**cls.DEFAULT_CONFIG, **user_config}
            config["output_dir"] = str(Path(config["output_dir"]).resolve())

            logger.info(f"✅ Loaded configuration from {cls.CONFIG_FILE}")
            return config
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"❌ Error loading config file: {e}. Using defaults.")
            return cls.DEFAULT_CONFIG

    @classmethod
    def save_default_config(cls):
        if not cls.CONFIG_FILE.exists():
            with cls.CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(cls.DEFAULT_CONFIG, f, indent=4)
            logger.info(f"✅ Default configuration file created: {cls.CONFIG_FILE}")

    @classmethod
    def save_config_updates(cls, updated_config: dict):
        try:
            with cls.CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(updated_config, f, indent=4)
            logger.info(f"✅ Configuration updated in {cls.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"❌ Failed to update configuration file: {e}")

# Ensure a default config exists upon import
ConfigManager.save_default_config()
