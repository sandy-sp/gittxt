import logging
import os

# Define the log directory in `src/gittxt-logs/`
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gittxt-logs")
LOG_FILE = os.path.join(LOG_DIR, "gittxt.log")

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,  # Default to INFO, changeable at runtime
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler(LOG_FILE, encoding="utf-8"),  # File output
    ],
)

def get_logger(name):
    """Returns a configured logger."""
    return logging.getLogger(name)
