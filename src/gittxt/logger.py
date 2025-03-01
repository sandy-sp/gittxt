import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# We assume you have these new config fields (or they default).
# For example, in config.py you might add:
#   "enable_file_logging": true,
#   "logging_level": "INFO", 
#   "max_log_bytes": 5000000,
#   "backup_count": 2
try:
    from gittxt.config import ConfigManager
except ImportError:
    ConfigManager = None  # Fallback if config isn't available, won't break logging

class Logger:
    """Handles logging configuration for Gittxt, including dynamic levels and rotating file logs."""

    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gittxt-logs")
    LOG_FILE = os.path.join(LOG_DIR, "gittxt.log")

    @staticmethod
    def setup_logger():
        """
        Configures the logging system:
         - Reads user config (if available) for logging_level, file logging toggles, etc.
         - Uses rotating file handler by default (5MB, 2 backups).
         - Logs to both console and (optionally) file.
         - ISO8601-like timestamps in log messages.
        """

        # Ensure the log directory exists
        os.makedirs(Logger.LOG_DIR, exist_ok=True)

        # Default fallback if config is not present
        default_logging_level = "INFO"
        default_enable_file_logging = True
        default_max_log_bytes = 5_000_000
        default_backup_count = 2

        # Attempt to load from Gittxt config
        if ConfigManager:
            config = ConfigManager.load_config()
            logging_level_str = config.get("logging_level", default_logging_level)
            enable_file_logging = config.get("enable_file_logging", default_enable_file_logging)
            max_log_bytes = config.get("max_log_bytes", default_max_log_bytes)
            backup_count = config.get("backup_count", default_backup_count)
        else:
            # If somehow config import fails, use defaults
            logging_level_str = default_logging_level
            enable_file_logging = default_enable_file_logging
            max_log_bytes = default_max_log_bytes
            backup_count = default_backup_count

        # Convert logging_level_str to a valid level (INFO if invalid)
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = level_map.get(logging_level_str.upper(), logging.INFO)

        # Create logging format with ISO-8601 style timestamps
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%dT%H:%M:%S%z"  # e.g. 2025-02-15T13:45:30+0000

        # Build a root logger with the chosen format/level
        logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)

        # Clear existing handlers added by basicConfig (we'll re-add them).
        # This ensures we don't duplicate logs if we re-run setup.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Create the console handler (always on)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
        console_handler.setFormatter(console_formatter)

        # Add console handler
        logging.root.addHandler(console_handler)

        # If file logging is enabled, set up rotating file handler
        if enable_file_logging:
            # Create rotating file handler
            rotating_file_handler = RotatingFileHandler(
                Logger.LOG_FILE,
                maxBytes=max_log_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            rotating_file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(log_format, datefmt=date_format)
            rotating_file_handler.setFormatter(file_formatter)
            logging.root.addHandler(rotating_file_handler)

    @staticmethod
    def get_logger(name):
        """Returns a configured logger instance."""
        return logging.getLogger(name)

if "-sp" in sys.argv:
    print("""
        🔥 **You've unlocked the Gittxt Easter Egg!** 🚀  
        🔗 Connect with me on LinkedIn: **[Sandeep Paidipati](https://www.linkedin.com/in/sandeep-paidipati/)**  
        📩 Add me & let's chat about anything!                                                                          
                                                                                                    
                                             888888                                                 
                                          888888888888                                              
                                        888888888888888                                             
                                       88888888    888888                                           
                                      8888888         8888                                          
                                      888888           8888                                         
                                      8888888            888                                        
                                       888888888          88                                        
                                        888888888888                                                
                                          88888888888888                                            
                                             88888888888888                                         
                                                 88888888888                                        
                                      88        66    88888888                                      
                                      8888     6666     8888888                                     
                                      88888   66666      888888                                     
                                       888888666666       88888                                     
                                        8888966666        888                                       
                                         888699698888888888888                                      
                                          9669668888888888888                                       
                                         666666988888888888                                         
                                        9666666                                                     
                                        666666                                                      
                                       6666666                                                      
                                      6666666                                                       
                                     6666669                                                        
                                    6666669                                                         
                                   6666666                                                          
                                  666669                                                            
                                  66                                                                
                                                                                                      
    """)
    sys.exit(0)  # Exit before running anything else

# Initialize logger on import
Logger.setup_logger()
