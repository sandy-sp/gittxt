from pathlib import Path
import json
import platform
import os
from gittxt.logger import Logger
from dotenv import load_dotenv

logger = Logger.get_logger(__name__)

# Load .env file if present
load_dotenv()


class ConfigManager:
    """Handles configuration loading and environment overrides."""

    SRC_DIR = Path(__file__).parent.resolve()
    CONFIG_FILE = SRC_DIR / "gittxt-config.json"

    @staticmethod
    def _determine_default_output_dir():
        system_name = platform.system().lower()
        home_dir = Path.home()
        if system_name.startswith("win") or system_name.startswith("darwin"):
            return (home_dir / "Documents" / "Gittxt").resolve()
        else:
            return (home_dir / "Gittxt").resolve()

    DEFAULT_CONFIG = {
        "output_dir": str(_determine_default_output_dir.__func__()),
        "size_limit": None,
        "include_patterns": [],
        "exclude_patterns": [".git", "node_modules", "__pycache__", ".log"],
        "output_format": "txt",
        "file_types": "code,docs",
        "logging_level": "INFO",
    }

    @classmethod
    def load_config(cls):
        config = cls.DEFAULT_CONFIG.copy()

        if cls.CONFIG_FILE.exists():
            try:
                with cls.CONFIG_FILE.open("r", encoding="utf-8") as f:
                    user_config = json.load(f)
                config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"❌ Error loading config file: {e}. Using defaults.")

        # .env overrides
        config["output_dir"] = os.getenv("GITTXT_OUTPUT_DIR", config["output_dir"])
        config["output_format"] = os.getenv(
            "GITTXT_OUTPUT_FORMAT", config["output_format"]
        )
        config["file_types"] = os.getenv("GITTXT_FILE_TYPES", config["file_types"])
        config["logging_level"] = os.getenv(
            "GITTXT_LOGGING_LEVEL", config["logging_level"]
        )
        config["size_limit"] = (
            int(os.getenv("GITTXT_SIZE_LIMIT", config["size_limit"] or 0)) or None
        )

        # Path normalization
        config["output_dir"] = str(Path(config["output_dir"]).resolve())

        logger.info("✅ Loaded configuration (with .env overrides if any)")
        return config

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


ConfigManager.save_default_config()
