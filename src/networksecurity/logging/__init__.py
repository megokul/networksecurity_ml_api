"""Initialize centralized logger for the `networksecurity.logging` package.

This sets up a reusable logger instance (`logger`) that can be imported
across the project to ensure consistent logging configuration.
"""

from .logger import setup_logger

# Create the logger once when the package is imported
logger = setup_logger()
