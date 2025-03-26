from pathlib import Path
import json
import platform
import os
from gittxt.core.logger import Logger
from dotenv import load_dotenv

logger = Logger.get_logger(__name__)

# Load .env file if present
load_dotenv()

class ConfigManager:
    """Handles main Gittxt configuration and environment overrides."""

    SRC_DIR = Path(__file__).resolve().parent
    CONFIG_FILE = SRC_DIR.parent / "config" / "gittxt-config.json"

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
        "exclude_dirs": [".git", "__pycache__", "node_modules", ".vscode", ".pytest_cache"],
        "output_format": "txt",
        "logging_level": "WARNING",
        "log_format": "plain",
        "auto_zip": False,
        "tree_exclude_dirs": [".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".vscode"],
        "scan_concurrency": 200
    }

    @classmethod
    def load_config(cls):
        config = cls.DEFAULT_CONFIG.copy()

        if cls.CONFIG_FILE.exists():
            try:
                with cls.CONFIG_FILE.open("r", encoding="utf-8") as f:
                    user_config = json.load(f)
                config.update(user_config)
                logger.info("✅ Loaded gittxt-config.json")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"⚠️ Could not load config file: {e}. Using defaults.")

        config["output_dir"] = os.getenv("GITTXT_OUTPUT_DIR", config["output_dir"])
        config["output_format"] = os.getenv("GITTXT_OUTPUT_FORMAT", config["output_format"])
        config["logging_level"] = os.getenv("GITTXT_LOGGING_LEVEL", config["logging_level"])
        config["log_format"] = os.getenv("GITTXT_LOG_FORMAT", config["log_format"])
        try:
            size_limit_val = os.getenv("GITTXT_SIZE_LIMIT", config["size_limit"])
            config["size_limit"] = int(size_limit_val) if size_limit_val is not None and size_limit_val != "" else None
        except ValueError:
            logger.warning(f"Invalid GITTXT_SIZE_LIMIT value: {os.getenv('GITTXT_SIZE_LIMIT')}. Using default.")
            config["size_limit"] = None
        auto_zip_val = os.getenv("GITTXT_AUTO_ZIP")
        if auto_zip_val is not None:
            config["auto_zip"] = auto_zip_val.lower() == "true"
        else:
            config["auto_zip"] = config["auto_zip"]
        config["output_dir"] = str(Path(config["output_dir"]).resolve())

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
    """Manages whitelist and blacklist of file types (only TEXTUAL can move)."""

    SRC_DIR = Path(__file__).parent.parent.resolve()
    FILETYPE_CONFIG_PATH = SRC_DIR / "config" / "filetype_config.json"

    DEFAULT_FILETYPE_CONFIG = {
        "whitelist": [".py", ".md", ".txt", ".html", ".json", ".yml", ".yaml", ".csv"],
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
            cls.FILETYPE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
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


if __name__ == "__main__":
    ConfigManager.save_default_config()
    FiletypeConfigManager.save_filetype_config(FiletypeConfigManager.load_filetype_config())
