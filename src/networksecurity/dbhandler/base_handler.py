from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


class DBHandler(ABC):
    """
    Abstract base class for all database or storage handlers.
    Enables unified behavior across MongoDB, CSV, PostgreSQL, S3, etc.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def close(self) -> None:
        """
        Clean up resources like DB connections or sessions.
        """
        pass

    @abstractmethod
    def load_from_source(self) -> pd.DataFrame:
        """
        Load and return a DataFrame from the underlying data source.
        Example:
            - MongoDB: collection
            - PostgreSQL: table
            - CSVHandler: file
            - S3Handler: object
        """
        pass

    def load_from_csv(self, source: Path) -> pd.DataFrame:
        """
        Generic utility: load a DataFrame from a CSV file.
        Available to all subclasses.
        """
        try:
            df = pd.read_csv(source)
            logger.info(f"DataFrame loaded from CSV: {source}")
            return df
        except Exception as e:
            logger.error(f"Failed to load DataFrame from CSV: {source}")
            raise NetworkSecurityError(e, logger) from e
