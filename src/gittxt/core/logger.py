import os
from pathlib import Path
import logging
import sys
import json
from logging.handlers import RotatingFileHandler

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

from gittxt.core.config import ConfigManager

class Logger:
    """
    Handles logging configuration for Gittxt, including optional JSON or colored logs.
    """

    BASE_DIR = Path(__file__).parent.parent.parent  # e.g., root of the repo
    LOG_DIR = BASE_DIR / "gittxt-logs"
    LOG_FILE = LOG_DIR / "gittxt.log"

    @staticmethod
    def _colorize(level, msg):
        if not colorama:
            return msg
        colors = {
            "DEBUG": colorama.Fore.CYAN,
            "INFO": colorama.Fore.GREEN,
            "WARNING": colorama.Fore.YELLOW,
            "ERROR": colorama.Fore.RED,
            "CRITICAL": colorama.Fore.MAGENTA,
        }
        reset = colorama.Style.RESET_ALL
        return f"{colors.get(level, '')}{msg}{reset}"

    @staticmethod
    def setup_logger(force_stdout=False):
        config = ConfigManager.load_config()
        Logger.LOG_DIR.mkdir(parents=True, exist_ok=True)

        log_level_str = os.getenv("GITTXT_LOGGING_LEVEL", config["logging_level"])
        log_format_style = os.getenv("GITTXT_LOG_FORMAT", config["log_format"]).lower()

        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        log_level = level_map.get(log_level_str.lower(), logging.WARNING)

        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        stream = sys.stdout if force_stdout else sys.stderr
        console_handler = logging.StreamHandler(stream)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(Logger._get_formatter(mode=log_format_style))
        root_logger.addHandler(console_handler)

        rotating_file_handler = RotatingFileHandler(Logger.LOG_FILE, maxBytes=5_000_000, backupCount=2, encoding="utf-8")
        rotating_file_handler.setLevel(log_level)
        rotating_file_handler.setFormatter(Logger._get_formatter(mode="plain"))  # always plain file logs
        root_logger.addHandler(rotating_file_handler)

    @staticmethod
    def _get_formatter(mode="plain"):
        if mode == "json":
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_record = {
                        "level": record.levelname,
                        "message": record.getMessage(),
                        "time": self.formatTime(record, self.datefmt),
                        "logger": record.name,
                    }
                    return json.dumps(log_record)
            return JSONFormatter("%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        else:
            class ColoredFormatter(logging.Formatter):
                def format(self, record):
                    msg = super().format(record)
                    return Logger._colorize(record.levelname, msg)
            return ColoredFormatter("%(levelname)s - %(message)s")

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

# Initialize at import
Logger.setup_logger()

# Optional Easter Egg if you want to keep it
if "-sp" in sys.argv:
    print(
        """
        🔥 **You've unlocked the Gittxt Easter Egg!** 🚀  
        🔗 Connect with me on LinkedIn: **[Sandeep Paidipati](https://www.linkedin.com/in/sandeep-paidipati/)**  
                                                                                                     
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
        """
        )
    sys.exit(0)
