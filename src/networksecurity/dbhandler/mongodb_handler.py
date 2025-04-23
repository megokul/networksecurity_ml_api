from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from pathlib import Path

from src.networksecurity.entity.config_entity import MongoHandlerConfig
from src.networksecurity.utils.core import csv_to_json_convertor, save_to_json
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.constants.constants import (
    MONGODB_CONNECT_TIMEOUT_MS,
    MONGODB_SOCKET_TIMEOUT_MS,
)

from src.networksecurity.dbhandler.base_handler import DBHandler


class MongoDBHandler(DBHandler):
    def __init__(self, config: MongoHandlerConfig):
        self.config = config
        self._client: MongoClient | None = None
        self._owns_client: bool = False

    def _get_client(self) -> MongoClient:
        if self._client is None:
            self._client = MongoClient(
                self.config.mongodb_uri,
                server_api=ServerApi("1"),
                connectTimeoutMS=MONGODB_CONNECT_TIMEOUT_MS,
                socketTimeoutMS=MONGODB_SOCKET_TIMEOUT_MS,
            )
            logger.info("MongoClient initialized.")
        return self._client

    def close(self) -> None:
        if self._client:
            self._client.close()
            logger.info("MongoClient connection closed.")
            self._client = None

    def ping_mongodb(self) -> None:
        try:
            self._get_client().admin.command("ping")
            logger.info("MongoDB ping successful.")
        except Exception as e:
            logger.error("MongoDB ping failed.")
            raise NetworkSecurityError(e, logger) from e

    def insert_csv_to_collection(self, csv_filepath: Path) -> int:
        try:
            records = csv_to_json_convertor(csv_filepath, self.config.json_data_filepath)

            # Save records as JSON using core utility
            save_to_json(records, self.config.json_data_filepath, label="Converted JSON Records")

            db = self._get_client()[self.config.database_name]
            collection = db[self.config.collection_name]
            result = collection.insert_many(records)
            logger.info(
                f"Inserted {len(result.inserted_ids)} records into "
                f"{self.config.database_name}.{self.config.collection_name}"
            )
            return len(result.inserted_ids)
        except Exception as e:
            logger.error("Failed to insert records into MongoDB.")
            raise NetworkSecurityError(e, logger) from e

    def load_from_source(self) -> pd.DataFrame:
        """
        Load data from the configured MongoDB collection as a pandas DataFrame.
        """
        try:
            db = self._get_client()[self.config.database_name]
            collection = db[self.config.collection_name]
            records = list(collection.find())
            df = pd.DataFrame(records)
            logger.info(
                f"Exported {len(df)} documents from "
                f"{self.config.database_name}.{self.config.collection_name} as DataFrame."
            )
            return df
        except Exception as e:
            logger.error("Failed to export data from MongoDB.")
            raise NetworkSecurityError(e, logger) from e
