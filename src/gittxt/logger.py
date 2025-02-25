import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,  # Change to DEBUG for more detailed logs
)

def get_logger(name):
    """Returns a configured logger."""
    return logging.getLogger(name)
