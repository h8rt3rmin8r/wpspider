import logging
import sys
import os
from datetime import datetime, timezone


class Iso8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc).astimezone()
        return dt.isoformat(timespec="seconds")

def setup_logging(log_file_path: str = "wpspider.log") -> logging.Logger:
    """
    Sets up the logging configuration for wpspider.
    Logs are written to the specified file and echoed to the console.
    """
    
    # Create logger
    logger = logging.getLogger("wpspider")
    logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times if function is called repeatedly
    if logger.handlers:
        return logger

    # Formatter
    formatter = Iso8601Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # File Handler
    # Ensure directory exists if path contains one
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
