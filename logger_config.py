import os
import logging
import sys # Import sys for stdout/stderr
from datetime import datetime
import pytz
import re
from logging.handlers import RotatingFileHandler # Import RotatingFileHandler

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
    Configure a global logger with console output (stdout for INFO, stderr for ERROR)
    and file output.
    """
    # Define your log directory and file path
    # Using PM2's default log directory is generally a good idea for applications
    # managed by PM2, or you can specify another path.
    # For daily-float-report, your logs are in /home/ubuntu/.pm2/logs/
    LOG_DIR = "/home/ubuntu/.pm2/logs"
    APP_NAME = "daily-float-report"
    LOG_FILE_PATH = os.path.join(LOG_DIR, f"{APP_NAME}.log") # Combined log file

    # Ensure the log directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) # Set the lowest level you want to capture anywhere

    # Clear any existing handlers to avoid duplicates on restarts
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define Thailand timezone (UTC+7) for consistent logging regardless of server timezone
    thai_tz = pytz.timezone('Asia/Bangkok')
    
    # Custom formatter class to handle timezone
    class TimezoneFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created)
            dt = thai_tz.localize(dt)
            if datefmt:
                return dt.strftime(datefmt)
            else:
                return dt.isoformat()
    
    # Create formatter with timezone-aware datetime
    formatter = TimezoneFormatter('[%(asctime)s] [%(levelname)s] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S %Z')

    sensitive_filter = SensitiveDataFilter()

    # --- Console Handler for INFO and above to STDOUT (PM2's .out.log) ---
    console_handler_stdout = logging.StreamHandler(sys.stdout)
    console_handler_stdout.setLevel(logging.INFO) # Only INFO and higher to stdout
    console_handler_stdout.setFormatter(formatter)
    console_handler_stdout.addFilter(sensitive_filter)
    logger.addHandler(console_handler_stdout)

    # --- Console Handler for ERROR and above to STDERR (PM2's .err.log) ---
    console_handler_stderr = logging.StreamHandler(sys.stderr)
    console_handler_stderr.setLevel(logging.ERROR) # Only ERROR and CRITICAL to stderr
    console_handler_stderr.setFormatter(formatter)
    console_handler_stderr.addFilter(sensitive_filter)
    logger.addHandler(console_handler_stderr)

    # --- File Handler for comprehensive logging to a dedicated file ---
    # This will log all levels (DEBUG and higher) to your specified log file.
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=10 * 1024 * 1024, # 10 MB per file
            backupCount=5              # Keep 5 backup files
        )
        file_handler.setLevel(logging.DEBUG) # Log all levels to the file
        file_handler.setFormatter(formatter)
        file_handler.addFilter(sensitive_filter)
        logger.addHandler(file_handler)
        logging.info(f"Logger initialized. All logs (DEBUG+) will be written to: {LOG_FILE_PATH}")
    except Exception as e:
        # If file logging fails (e.g., permissions), log to stderr and console only
        logger.error(f"Failed to initialize file logger at {LOG_FILE_PATH}: {e}", exc_info=True)
        logger.warning("File logging disabled. Using console logging only (stdout for INFO, stderr for ERROR).")

    logging.info("Logger setup complete.") # This will go to .out.log now
    return logger

# Define custom log functions for maintaining the style used in the codebase
# These will use the root logger configured above
def log_info(message):
    logging.info(f"{message}")

def log_debug(message):
    logging.debug(f"{message}")

def log_success(message):
    logging.info(f"[SUCCESS] {message}") # Success is typically an info level

def log_error(message):
    logging.error(f"{message}")

def log_warning(message):
    logging.warning(f"{message}")

def log_wait(message):
    logging.info(f"[WAIT] {message}") # Wait is typically an info level

# Setup logger when importing this module
logger = setup_logger()