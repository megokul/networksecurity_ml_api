"""
Initialize centralized logger for the `networksecurity.logging` package.

This module sets up a reusable logger instance (`logger`) that can be imported
across the project to ensure consistent, centralized logging configuration.

Supports:
- Shared UTC timestamp for file/folder naming
- Dynamic logger name via environment variable
- Dynamic log level via environment variable
"""

import os
import logging

from .logger import setup_logger

# Use env variable for logger name, default to "networksecurity"
LOGGER_NAME = os.getenv("LOGGER_NAME", "networksecurity")

# Use env variable for log level, default to "DEBUG"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# Initialize and configure the logger
logger = setup_logger(name=LOGGER_NAME)
logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
