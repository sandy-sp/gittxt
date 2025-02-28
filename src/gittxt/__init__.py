import os
from gittxt.logger import Logger
from gittxt.config import ConfigManager

# Package Metadata
__version__ = "1.2.0"
__author__ = "Sandeep Paidipati"
__description__ = "CLI tool for extracting text from Git repositories"

logger = Logger.get_logger(__name__)

# Load Configuration
config = ConfigManager.load_config()

# Define core directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../gittxt-logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "../gittxt-outputs")
CACHE_DIR = os.path.join(OUTPUT_DIR, "cache")
TEXT_DIR = os.path.join(OUTPUT_DIR, "text")
JSON_DIR = os.path.join(OUTPUT_DIR, "json")

# Ensure necessary directories exist
for directory in [LOG_DIR, OUTPUT_DIR, CACHE_DIR, TEXT_DIR, JSON_DIR]:
    os.makedirs(directory, exist_ok=True)

logger.info("✅ Gittxt package initialized successfully.")
logger.info(f"📂 Output Directory: {OUTPUT_DIR}")
logger.info(f"📂 Log Directory: {LOG_DIR}")
logger.info(f"🔹 Version: {__version__}")
