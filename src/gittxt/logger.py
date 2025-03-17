from pathlib import Path
import logging
import sys
from logging.handlers import RotatingFileHandler

try:
    from gittxt.config import ConfigManager
except ImportError:
    ConfigManager = None  # fallback

try:
    import colorama

    colorama.init()
except ImportError:
    colorama = None  # fallback if colorama is not available


class Logger:
    """Handles logging configuration for Gittxt, including colored CLI output."""

    BASE_DIR = Path(__file__).parent.parent.resolve()
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
        color = colors.get(level, "")
        return f"{color}{msg}{reset}"

    @staticmethod
    def setup_logger():
        Logger.LOG_DIR.mkdir(parents=True, exist_ok=True)

        config = ConfigManager.load_config() if ConfigManager else {}
        log_level_str = config.get("logging_level", "INFO")

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        log_level = level_map.get(log_level_str.upper(), logging.INFO)

        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(Logger._get_cli_formatter())
        logging.root.addHandler(console_handler)

        # File Handler
        rotating_file_handler = RotatingFileHandler(
            Logger.LOG_FILE, maxBytes=5_000_000, backupCount=2, encoding="utf-8"
        )
        rotating_file_handler.setLevel(log_level)
        rotating_file_handler.setFormatter(
            logging.Formatter(log_format, datefmt=date_format)
        )
        logging.root.addHandler(rotating_file_handler)

    @staticmethod
    def _get_cli_formatter():
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                msg = super().format(record)
                return Logger._colorize(record.levelname, msg)

        return ColoredFormatter("%(levelname)s - %(message)s")

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)


Logger.setup_logger()

if "-sp" in sys.argv:
    print(
        """
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
    """
    )
    sys.exit(0)
