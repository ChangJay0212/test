"""
Logger module for centralized logging configuration
"""
import logging
import logging.config
from pathlib import Path

def setup_logger(name: str = "agentic_system") -> logging.Logger:
    """
    Set up logger with configuration from logging.conf.
    
    Args:
        name (str): Logger name. Defaults to "agentic_system".
        
    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception:
            An error occurred while setting up the logger.
    """
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Load logging configuration
    config_path = Path(__file__).parent.parent / "config" / "logging.conf"
    if config_path.exists():
        logging.config.fileConfig(config_path)
    else:
        # Fallback configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/agentic_system.log'),
                logging.StreamHandler()
            ]
        )
    
    return logging.getLogger(name)

# Create default logger instance
logger = setup_logger()
