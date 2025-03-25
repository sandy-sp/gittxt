from pathlib import Path
from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager
from gittxt.core.constants import TEXT_DIR, JSON_DIR, MD_DIR, ZIP_DIR, TEMP_DIR

# Package Metadata
__version__ = "1.6.0"
__author__ = "Sandeep Paidipati"
__description__ = "Gittxt: Get text from Git repositories in AI-ready formats"

# Initialize logger + load config
logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

# Define output base directories
BASE_DIR = Path(__file__).parent.resolve()
LOG_DIR = (BASE_DIR / "../gittxt-logs").resolve()
OUTPUT_DIR = Path(config.get("output_dir")).resolve()
TEXT_DIR = OUTPUT_DIR / TEXT_DIR
JSON_DIR = OUTPUT_DIR / JSON_DIR
MD_DIR = OUTPUT_DIR / MD_DIR
ZIP_DIR = OUTPUT_DIR / ZIP_DIR
TEMP_DIR = OUTPUT_DIR / TEMP_DIR

# Auto-create necessary folders
for directory in [LOG_DIR, OUTPUT_DIR, TEXT_DIR, JSON_DIR, MD_DIR, ZIP_DIR, TEMP_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning(f"⚠️ Failed to create directory {directory}: {e}")

logger.info("✅ Gittxt initialized successfully.")
logger.info(f"📂 Output Directory: {OUTPUT_DIR}")
logger.info(f"📂 Log Directory: {LOG_DIR}")
logger.info(f"🔹 Version: {__version__}")
