import logging
import os

class Logger:
    """Handles logging configuration for Gittxt."""

    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gittxt-logs")
    LOG_FILE = os.path.join(LOG_DIR, "gittxt.log")

    @staticmethod
    def setup_logger():
        """Configures logging system."""
        # Ensure the log directory exists
        os.makedirs(Logger.LOG_DIR, exist_ok=True)

        # Create logging format
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            format=log_format,
            level=logging.INFO,  # Default level (can be changed at runtime)
            handlers=[
                logging.StreamHandler(),  # Console output
                logging.FileHandler(Logger.LOG_FILE, encoding="utf-8"),  # File output
            ],
        )

    @staticmethod
    def get_logger(name):
        """Returns a configured logger instance."""
        return logging.getLogger(name)

# Initialize logger on import
Logger.setup_logger()
