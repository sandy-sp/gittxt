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
    """Handles main Gittxt configuration and environment overrides."""

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

    # 🟢 DEFAULT CONFIG with new keys added
    DEFAULT_CONFIG = {
        "output_dir": str(_determine_default_output_dir.__func__()),
        "size_limit": None,
        "include_patterns": [],
        "exclude_patterns": [".git", "node_modules", "__pycache__", ".log"],
        "custom_exclude_patterns": [],
        "output_format": "txt",
        "file_types": "code,docs",
        "logging_level": "WARNING",
        "log_format": "plain",        # ✅ ADDED
        "auto_zip": False             # ✅ ADDED
    }

    @classmethod
    def load_config(cls):
        config = cls.DEFAULT_CONFIG.copy()

        # Step 1: Load from gittxt-config.json if present
        if cls.CONFIG_FILE.exists():
            try:
                with cls.CONFIG_FILE.open("r", encoding="utf-8") as f:
                    user_config = json.load(f)
                config.update(user_config)
                logger.info(f"✅ Loaded gittxt-config.json")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"⚠️ Could not load config file: {e}. Using defaults.")

        # Step 2: .env overrides
        config["output_dir"] = os.getenv("GITTXT_OUTPUT_DIR", config["output_dir"])
        config["output_format"] = os.getenv("GITTXT_OUTPUT_FORMAT", config["output_format"])
        config["file_types"] = os.getenv("GITTXT_FILE_TYPES", config["file_types"])
        config["logging_level"] = os.getenv("GITTXT_LOGGING_LEVEL", config["logging_level"])
        config["log_format"] = os.getenv("GITTXT_LOG_FORMAT", config["log_format"])
        config["size_limit"] = (
            int(os.getenv("GITTXT_SIZE_LIMIT", config["size_limit"] or 0)) or None
        )
        config["auto_zip"] = os.getenv("GITTXT_AUTO_ZIP", str(config["auto_zip"])).lower() == "true"

        # Step 3: Path normalization
        config["output_dir"] = str(Path(config["output_dir"]).resolve())

        # Step 4: Merge default excludes + custom excludes
        merged_excludes = set(config["exclude_patterns"]) | set(config.get("custom_exclude_patterns", []))
        config["exclude_patterns"] = sorted(merged_excludes)

        logger.info("✅ Final config loaded (env + json + defaults merged)")
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


class FiletypeConfigManager:
    """Handles loading and saving filetype_config.json (whitelist/blacklist)"""

    SRC_DIR = Path(__file__).parent.resolve()
    FILETYPE_CONFIG_PATH = SRC_DIR / "filetype_config.json"

    DEFAULT_FILETYPE_CONFIG = {
        "whitelist": [],
        "blacklist": [".zip", ".exe", ".bin", ".docx", ".xls", ".pdf"]
    }

    @classmethod
    def load_filetype_config(cls) -> dict:
        if cls.FILETYPE_CONFIG_PATH.exists():
            try:
                with cls.FILETYPE_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Could not load filetype config: {e}. Using defaults.")
        return cls.DEFAULT_FILETYPE_CONFIG.copy()

    @classmethod
    def save_filetype_config(cls, config: dict):
        try:
            with cls.FILETYPE_CONFIG_PATH.open("w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            logger.info(f"✅ Updated filetype config: {cls.FILETYPE_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"❌ Failed to update filetype config: {e}")

    @classmethod
    def add_to_whitelist(cls, ext: str):
        config = cls.load_filetype_config()
        if ext not in config["whitelist"]:
            config["whitelist"].append(ext)
            cls.save_filetype_config(config)

    @classmethod
    def add_to_blacklist(cls, ext: str):
        config = cls.load_filetype_config()
        if ext not in config["blacklist"]:
            config["blacklist"].append(ext)
            cls.save_filetype_config(config)


# Initial bootstrapping
ConfigManager.save_default_config()
FiletypeConfigManager.save_filetype_config(FiletypeConfigManager.load_filetype_config())
