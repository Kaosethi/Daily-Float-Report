"""
Central logging configuration for Daily Float Report
Provides consistent, timestamped logs with clear issue identification
"""

import os
import sys
import logging
import datetime
from logging.handlers import TimedRotatingFileHandler
from functools import wraps

# Constants
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
LOG_FORMAT = '[%(asctime)s][%(levelname)8s][%(module)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
ERROR_PREFIX = '❌ ERROR: '
WARNING_PREFIX = '⚠️ WARNING: '
SUCCESS_PREFIX = '✅ SUCCESS: '
INFO_PREFIX = 'ℹ️ '
DEBUG_PREFIX = '🔍 '

# Console colors for better readability
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'

# Custom formatter with colors for console
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        message = super().format(record)
        
        if levelname == 'ERROR' or levelname == 'CRITICAL':
            return f"{Colors.RED}{message}{Colors.RESET}"
        elif levelname == 'WARNING':
            return f"{Colors.YELLOW}{message}{Colors.RESET}"
        elif levelname == 'INFO':
            return f"{Colors.GREEN}{message}{Colors.RESET}"
        elif levelname == 'DEBUG':
            return f"{Colors.CYAN}{message}{Colors.RESET}"
        else:
            return message

# Configure the main logger
def setup_logger(name='float_report', log_level=logging.INFO):
    """Set up and return a logger with file and console handlers"""
    # Create logs directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Get today's date for the log filename
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOG_DIR, f'{name}_{today}.log')
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        log_file, when='midnight', backupCount=30, encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create the default logger instance
logger = setup_logger()

# Convenience functions for common logging patterns
def log_error(message, exc_info=None):
    """Log an error with clear prefix and optional exception info"""
    if exc_info:
        logger.error(f"{ERROR_PREFIX}{message}", exc_info=exc_info)
    else:
        logger.error(f"{ERROR_PREFIX}{message}")

def log_warning(message):
    """Log a warning with clear prefix"""
    logger.warning(f"{WARNING_PREFIX}{message}")

def log_success(message):
    """Log a success message with clear prefix"""
    logger.info(f"{SUCCESS_PREFIX}{message}")

def log_info(message):
    """Log an informational message with clear prefix"""
    logger.info(f"{INFO_PREFIX}{message}")

def log_debug(message):
    """Log a debug message with clear prefix"""
    logger.debug(f"{DEBUG_PREFIX}{message}")

def log_step(step_name):
    """Log the start of a processing step"""
    logger.info(f"==== STARTING STEP: {step_name} ====")

# Function decorator for logging function entry/exit and timing
def log_function(func):
    """Decorator to log function calls with execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Entering function: {func_name}")
        start_time = datetime.datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.datetime.now() - start_time).total_seconds()
            logger.debug(f"Exited function: {func_name} (took {duration:.2f}s)")
            return result
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            logger.error(f"Error in {func_name} after {duration:.2f}s: {str(e)}", exc_info=True)
            raise
            
    return wrapper

# Context manager for logging blocks of code
class LogContext:
    """Context manager for logging code blocks with timing"""
    def __init__(self, name):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.datetime.now()
        logger.debug(f"Starting context: {self.name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            logger.error(f"Error in context {self.name} after {duration:.2f}s: {exc_val}", exc_info=(exc_type, exc_val, exc_tb))
        else:
            logger.debug(f"Completed context: {self.name} (took {duration:.2f}s)")
        
        return False  # Don't suppress exceptions
