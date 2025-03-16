from pathlib import Path
from gittxt.logger import Logger
from gittxt.config import ConfigManager

# Package Metadata
__version__ = "1.3.1"
__author__ = "Sandeep Paidipati"
__description__ = "Get Text of Your Repo for AI, LLMs & Docs!"

logger = Logger.get_logger(__name__)

# Load Configuration
config = ConfigManager.load_config()

# Define core directories using pathlib
BASE_DIR = Path(__file__).parent.resolve()
LOG_DIR = (BASE_DIR / "../gittxt-logs").resolve()
OUTPUT_DIR = Path(config.get("output_dir")).resolve()
CACHE_DIR = OUTPUT_DIR / "cache"
TEXT_DIR = OUTPUT_DIR / "text"
JSON_DIR = OUTPUT_DIR / "json"
MD_DIR = OUTPUT_DIR / "md"

# Ensure necessary directories exist
for directory in [LOG_DIR, OUTPUT_DIR, CACHE_DIR, TEXT_DIR, JSON_DIR, MD_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

logger.info("✅ Gittxt package initialized successfully.")
logger.info(f"📂 Output Directory: {OUTPUT_DIR}")
logger.info(f"📂 Log Directory: {LOG_DIR}")
logger.info(f"🔹 Version: {__version__}")
