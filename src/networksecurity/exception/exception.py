"""Custom exception and logger interface for the phishing detection web app.

This module defines:
- LoggerInterface: a structural protocol for logging
- NetworkSecurityError: a traceback-aware exception with logging support
"""


import sys
from typing import Protocol


class LoggerInterface(Protocol):
    """A structural interface that defines the logger's required methods.

    Any logger passed to NetworkSecurityException must implement this interface.
    """

    def error(self, message: str) -> None:
        """Log an error-level message."""
        ...


class NetworkSecurityError(Exception):
    """Custom exception class for the phishing detection web application.

    Captures traceback details and logs the error using the provided logger.
    """

    def __init__(self, error_message: Exception, logger: LoggerInterface) -> None:
        """Initialize the exception and log it using the injected logger.

        Args:
            error_message (Exception): The original caught exception.
            logger (LoggerInterface): A logger that supports an `error(str)` method.

        """
        super().__init__(str(error_message))
        self.error_message: str = str(error_message)

        # Get traceback info from sys
        _, _, exc_tb = sys.exc_info()
        self.lineno: int | None = exc_tb.tb_lineno if exc_tb else None
        self.file_name: str | None = (
            exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown"
        )

        # Log the formatted error
        logger.error(str(self))

    def __str__(self) -> str:
        """Return a formatted error message with file name and line number."""
        return (
            f"Error occurred in file [{self.file_name}], "
            f"line [{self.lineno}], "
            f"message: [{self.error_message}]"
        )
