import os
from gittxt.logger import Logger
from gittxt.config import ConfigManager

# Package Metadata
__version__ = "1.3.1"
__author__ = "Sandeep Paidipati"
__description__ = "Get Text of Your Repo for AI, LLMs & Docs!"

logger = Logger.get_logger(__name__)

# Load Configuration
config = ConfigManager.load_config()

# Define core directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../gittxt-logs")
# Use the output_dir from config (which is now OS-aware), with fallback if needed.
OUTPUT_DIR = config.get("output_dir", os.path.abspath(os.path.join(BASE_DIR, "../gittxt-outputs")))
CACHE_DIR = os.path.join(OUTPUT_DIR, "cache")
TEXT_DIR = os.path.join(OUTPUT_DIR, "text")
JSON_DIR = os.path.join(OUTPUT_DIR, "json")
MD_DIR = os.path.join(OUTPUT_DIR, "md")  # New directory for markdown output

# Ensure necessary directories exist
for directory in [LOG_DIR, OUTPUT_DIR, CACHE_DIR, TEXT_DIR, JSON_DIR, MD_DIR]:
    os.makedirs(directory, exist_ok=True)

logger.info("✅ Gittxt package initialized successfully.")
logger.info(f"📂 Output Directory: {OUTPUT_DIR}")
logger.info(f"📂 Log Directory: {LOG_DIR}")
logger.info(f"🔹 Version: {__version__}")
