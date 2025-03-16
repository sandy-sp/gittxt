from pathlib import Path
import logging
import sys
from logging.handlers import RotatingFileHandler

try:
    from gittxt.config import ConfigManager
except ImportError:
    ConfigManager = None  # Fallback if config isn't available

class Logger:
    """Handles logging configuration for Gittxt, including dynamic levels and rotating file logs."""

    BASE_DIR = Path(__file__).parent.parent.resolve()
    LOG_DIR = BASE_DIR / "gittxt-logs"
    LOG_FILE = LOG_DIR / "gittxt.log"

    @staticmethod
    def setup_logger():
        Logger.LOG_DIR.mkdir(parents=True, exist_ok=True)

        default_logging_level = "INFO"
        default_enable_file_logging = True
        default_max_log_bytes = 5_000_000
        default_backup_count = 2

        if ConfigManager:
            config = ConfigManager.load_config()
            logging_level_str = config.get("logging_level", default_logging_level)
            enable_file_logging = config.get("enable_file_logging", default_enable_file_logging)
            max_log_bytes = config.get("max_log_bytes", default_max_log_bytes)
            backup_count = config.get("backup_count", default_backup_count)
        else:
            logging_level_str = default_logging_level
            enable_file_logging = default_enable_file_logging
            max_log_bytes = default_max_log_bytes
            backup_count = default_backup_count

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
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
    sys.exit(0)

Logger.setup_logger()




   