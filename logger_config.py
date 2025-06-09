import os
import logging
from datetime import datetime
import pytz
import re

class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive information from log messages"""
    
    def __init__(self):
        super().__init__()
        # Patterns to look for in log messages
        self.patterns = [
            # Passwords and credentials
            (re.compile(r'\b(password|PASSWORD)\s*[=:]\s*["\']?([^"\',\s]+)["\']?', re.IGNORECASE), '***REDACTED***'),
            (re.compile(r'\b(username|USERNAME)\s*[=:]\s*["\']?([^"\',\s]+)["\']?', re.IGNORECASE), '***REDACTED***'),
            (re.compile(r'\b(api_key|API_KEY|apikey)\s*[=:]\s*["\']?([^"\',\s]+)["\']?', re.IGNORECASE), '***REDACTED***'),
            
            # SendGrid API key pattern
            (re.compile(r'\b(SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43})\b'), '***SENDGRID-KEY-REDACTED***'),
            
            # Balance numbers (optionally)
            # (re.compile(r'\b(Balance|balance):\s*([0-9,.]+)\s*THB\b'), r'\1: ***REDACTED*** THB'),
        ]
    
    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Apply each pattern to the message
            for pattern, replacement in self.patterns:
                record.msg = pattern.sub(replacement, record.msg)
                
            # Also redact in formatted message if it already exists
            if hasattr(record, 'message'):
                for pattern, replacement in self.patterns:
                    record.message = pattern.sub(replacement, record.message)
        return True

def setup_logger():
    """
    Configure a global logger with console output only
    """
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler with INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter with datetime
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    
    # Add sensitive data filter to handler
    sensitive_filter = SensitiveDataFilter()
    console_handler.addFilter(sensitive_filter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    logging.info("Logger initialized (console logging only)")
    return logger

# Define custom log functions for maintaining the style used in the codebase
def log_info(message):
    logging.info(f"{message}")

def log_debug(message):
    logging.debug(f"{message}")

def log_success(message):
    logging.info(f"[SUCCESS] {message}")

def log_error(message):
    logging.error(f"{message}")

def log_warning(message):
    logging.warning(f"{message}")

def log_wait(message):
    logging.info(f"[WAIT] {message}")

# Setup logger when importing this module
logger = setup_logger()
