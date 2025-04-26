"""
Logging utility module.

Provides `setup_logger()` to configure a logger with both a file and stream handler,
using a UTC timestamp synchronized across the pipeline (logs, artifacts, models, etc.).
"""

import logging
import sys
from pathlib import Path

from src.networksecurity.constants.constants import LOGS_ROOT
from src.networksecurity.utils.timestamp import get_shared_utc_timestamp

def setup_logger(name: str = "app_logger") -> logging.Logger:
    """
    Set up and return a logger instance with a consistent timestamped log directory and file.

    Ensures:
    - One timestamp per pipeline run (shared with ConfigurationManager)
    - No duplicate handlers on repeated setup
    - Clean log formatting to stdout and file

    Args:
        name (str): The name of the logger instance (e.g., 'data_ingestion').

    Returns:
        logging.Logger: Configured logger with file and stream handlers.
    """
    sys.stdout.reconfigure(encoding='utf-8')

    # Get shared timestamp for this run
    timestamp = get_shared_utc_timestamp()

    # Log folder: logs/<timestamp>/
    log_dir = Path(LOGS_ROOT) / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file: logs/<timestamp>/<timestamp>.log
    log_filepath = log_dir / f"{timestamp}.log"

    # Log message format
    log_format = "[%(asctime)s] - %(levelname)s - %(module)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Add file handler if not already added
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(log_filepath)
               for h in logger.handlers):
        file_handler = logging.FileHandler(log_filepath, mode="a")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add stdout stream handler if not already added
    if not any(isinstance(h, logging.StreamHandler) and h.stream == sys.stdout
               for h in logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


# Example usage
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("Logger initialized successfully.")
