from pathlib import Path
import json
import platform
import os
from dotenv import load_dotenv
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
import logging

logger = logging.getLogger("gittxt.config")

# Load .env if present
load_dotenv()

class ConfigManager:
    """
    Manages main Gittxt configuration from:
      1. default values (in code)
      2. gittxt-config.json
      3. environment variables
    """

    SRC_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = SRC_DIR.parent / "config"  # e.g. src/gittxt/config/
    CONFIG_FILE = CONFIG_DIR / "gittxt-config.json"

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
        # Consolidate all top-level excludes here; references constants.py if you like
        "exclude_dirs": EXCLUDED_DIRS_DEFAULT,
        "output_format": "txt",
        "logging_level": "WARNING",
        "log_format": "plain",
        "auto_zip": False,
        # If you want to store tree excludes separately:
        "tree_exclude_dirs": [".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".vscode"],
        "scan_concurrency": 200
    }

    @classmethod
    def load_config(cls):
        config = cls.DEFAULT_CONFIG.copy()

        # Step 1: load from config file
        if cls.CONFIG_FILE.exists():
            try:
                with cls.CONFIG_FILE.open("r", encoding="utf-8") as f:
                    user_config = json.load(f)
                config.update(user_config)
                logger.info("✅ Loaded gittxt-config.json")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"⚠️ Could not load config file: {e}. Using defaults.")

        # Step 2: environment overrides
        config["output_dir"] = os.getenv("GITTXT_OUTPUT_DIR", config["output_dir"])
        config["output_format"] = os.getenv("GITTXT_OUTPUT_FORMAT", config["output_format"])
        config["logging_level"] = os.getenv("GITTXT_LOGGING_LEVEL", config["logging_level"])
        config["log_format"] = os.getenv("GITTXT_LOG_FORMAT", config["log_format"])

        # Convert size limit to int or None
        size_limit_val = os.getenv("GITTXT_SIZE_LIMIT", str(config["size_limit"]))
        if size_limit_val.isdigit():
            config["size_limit"] = int(size_limit_val)
        else:
            config["size_limit"] = None

        # Auto-zip env
        auto_zip_val = os.getenv("GITTXT_AUTO_ZIP")
        if auto_zip_val is not None:
            config["auto_zip"] = (auto_zip_val.lower() == "true")

        # Path normalization
        config["output_dir"] = str(Path(config["output_dir"]).resolve())

        logger.info("✅ Final config loaded from default + file + env.")
        return config

    @classmethod
    def save_default_config(cls):
        """
        Create a default config file if one does not exist.
        """
        if not cls.CONFIG_FILE.exists():
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with cls.CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(cls.DEFAULT_CONFIG, f, indent=4)
            logger.info(f"✅ Default configuration file created at {cls.CONFIG_FILE}")

    @classmethod
    def save_config_updates(cls, updated_config: dict):
        """
        Persist changes to gittxt-config.json. 
        """
        try:
            with cls.CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(updated_config, f, indent=4)
            logger.info(f"✅ Configuration updated in {cls.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"❌ Failed to update configuration file: {e}")
