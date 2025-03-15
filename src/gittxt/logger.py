import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from gittxt.config import ConfigManager

class Logger:
    """
    Handles logging configuration for Gittxt, including dynamic levels, rotating file logs,
    and optional verbose/debug modes.
    """
    
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
         - Adds a VERBOSE mode for additional debugging insights.
        """
        
        os.makedirs(Logger.LOG_DIR, exist_ok=True)

        # Default settings
        default_config = {
            "logging_level": "INFO",
            "enable_file_logging": True,
            "max_log_bytes": 5_000_000,
            "backup_count": 2,
            "verbose": False,  # New flag for verbose mode
            "log_file": Logger.LOG_FILE  # Allowing custom log file
        }
        
        config = ConfigManager.load_config() if ConfigManager else default_config
        logging_level_str = config.get("logging_level", default_config["logging_level"])
        enable_file_logging = config.get("enable_file_logging", default_config["enable_file_logging"])
        max_log_bytes = config.get("max_log_bytes", default_config["max_log_bytes"])
        backup_count = config.get("backup_count", default_config["backup_count"])
        verbose = config.get("verbose", default_config["verbose"])
        log_file = config.get("log_file", default_config["log_file"])

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "VERBOSE": logging.DEBUG if verbose else logging.INFO,  # VERBOSE mode
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = level_map.get(logging_level_str.upper(), logging.INFO)

        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%dT%H:%M:%S%z"

        logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)
        
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
        console_handler.setFormatter(console_formatter)
        logging.root.addHandler(console_handler)

        if enable_file_logging:
            rotating_file_handler = RotatingFileHandler(
                log_file, maxBytes=max_log_bytes, backupCount=backup_count, encoding="utf-8"
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
