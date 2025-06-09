import os
import logging
from datetime import datetime
import pytz

def setup_logger():
    """
    Configure a global logger with both console and file output
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler with higher level (INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create file handler for all logs
    bangkok_tz = pytz.timezone("Asia/Bangkok")
    today = datetime.now(bangkok_tz).strftime('%Y-%m-%d')
    log_file = os.path.join(logs_dir, f"daily_float_report_{today}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter with datetime
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logging.info(f"Logger initialized. Log file: {log_file}")
    return logger

# Define custom log functions for maintaining the style used in the codebase
def log_info(message):
    logging.info(f"[INFO] {message}")

def log_debug(message):
    logging.debug(f"[DEBUG] {message}")

def log_success(message):
    logging.info(f"✅ {message}")

def log_error(message):
    logging.error(f"❌ {message}")

def log_warning(message):
    logging.warning(f"⚠️ {message}")

def log_wait(message):
    logging.info(f"[WAIT] {message}")

# Setup logger when importing this module
logger = setup_logger()
