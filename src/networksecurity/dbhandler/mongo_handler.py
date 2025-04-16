from pymongo import MongoClient
from pymongo.server_api import ServerApi
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.entity.config_entity import MongoHandlerConfig
from src.networksecurity.utils.common import csv_to_json_convertor

import pandas as pd
import numpy as np
from pathlib import Path

class MongoDBHandler:
    def __init__(self, config: MongoHandlerConfig):
        self.config = config

    def ping_mongodb(self):
        client = MongoClient(self.config.mongodb_uri, server_api=ServerApi("1"))
        try:
            client.admin.command("ping")
            logger.info("MongoDB ping successful.")
        except Exception as e:
            logger.error("MongoDB ping failed.")
            raise NetworkSecurityError(e, logger) from e

    def insert_csv_to_collection(self, csv_filepath: Path) -> int:
        try:
            records = csv_to_json_convertor(csv_filepath, self.config.json_data_filepath)
            client = MongoClient(self.config.mongodb_uri)
            db = client[self.config.database_name]
            collection = db[self.config.collection_name]
            result = collection.insert_many(records)
            logger.info(f"Inserted {len(result.inserted_ids)} records into MongoDB.")
            return len(result.inserted_ids)
        except Exception as e:
            logger.error("Failed to insert records into MongoDB.")
            raise NetworkSecurityError(e, logger) from e

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        try:
            client = MongoClient(self.config.mongodb_uri)
            db = client[self.config.database_name]
            collection = db[self.config.collection_name]
            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)
            df.replace({"na": np.nan}, inplace=True)
            logger.info("Exported collection from MongoDB as DataFrame.")
            return df
        except Exception as e:
            logger.error("Failed to export data from MongoDB.")
            raise NetworkSecurityError(e, logger) from e