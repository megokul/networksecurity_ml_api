"""Logging utility module.

This module provides a reusable `setup_logger()` function that configures
a logger with both a timestamped file handler and a console stream handler.
It ensures no duplicate handlers are added, even if the logger is reused.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


def setup_logger(name: str = "app_logger") -> logging.Logger:
    """Set up and return a logger instance with timestamped file and stream handlers.

    This function creates a logs directory with a timestamp,
    configures a logger to write logs to a file and also to stdout,
    and ensures no duplicate handlers are added.

    Args:
        name (str): The name of the logger. Default is "app_logger".

    Returns:
        logging.Logger: Configured logger instance.

    """
    # Define the log message format (includes timestamp, level, module, and message)
    log_format = "[%(asctime)s] - %(levelname)s - %(module)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Generate a timestamp string in UTC to use in log file and directory names
    timestamp = datetime.now(timezone.utc).strftime("%Y_%m_%dT%H_%M_%S")

    # Create a folder named with the timestamp under the "logs" directory
    log_dir = Path("logs") / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    # Define the full path for the timestamped log file
    log_filepath = log_dir / f"{timestamp}.log"

    # Create or retrieve a logger instance with the given name (reused if already created)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set logging level to DEBUG for maximum detail

    # Only add file handler if it's not already attached (avoid duplicates)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        file_handler = logging.FileHandler(log_filepath, mode="a")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Only add stream handler for stdout if it's not already attached
    if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
               for h in logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


# Example usage (only runs when this module is executed as the main program)
if __name__ == "__main__":
    # Repeated calls to setup_logger() with the same name won't add duplicate handlers.
    logger = setup_logger()
    logger.info("Logger is set up and ready.")
