import logging
import os
import sys

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
