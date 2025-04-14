

from src.networksecurity.entity.config_entity import DataIngestionConfig, MongoHandlerConfig
from src.networksecurity.exception.exception import NetworkSecurityError
import os
import sys
import numpy as np
import pandas as pd
from pymongo import MongoClient
from src.networksecurity.logging import logger
from dotenv import load_dotenv
from src.networksecurity.dbhandler.mongo_handler import MongoDBHandler
from pathlib import Path
from src.networksecurity.utils.common import csv_to_json_convertor, create_directories, replace_username_password_in_uri

load_dotenv()

class DataIngestion:

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.config=data_ingestion_config
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def load_data_from_mongo(self) -> pd.DataFrame:
        """Connects to MongoDB using config and saves data to the staging directory."""
        try:
            logger.info("Connecting to MongoDB...")

            mongodb_uri_base = os.getenv("MONGODB_URI_BASE")
            mongodb_username = os.getenv("MONGODB_USERNAME")
            mongodb_password = os.getenv("MONGODB_PASSWORD")

            mongodb_uri = replace_username_password_in_uri(
                mongodb_uri_base, mongodb_username, mongodb_password
            )

            client = MongoClient(mongodb_uri)

            database_name = os.getenv("DATABASE_NAME")
            collection_name = os.getenv("COLLECTION_NAME")

            database = client[database_name]
            collection = database[collection_name]

            logger.info(f"Reading data from MongoDB: '{database_name}/{collection_name}'")
            raw_data_df = pd.DataFrame(list(collection.find()))

            featurestore_dir = self.config.featurestore_dir
            create_directories(featurestore_dir)
            csv_path = Path(featurestore_dir) / "raw_data.csv"
            raw_data_df.to_csv(csv_path, index=False)

            if "_id" in raw_data_df.columns:
                ingested_data_df = raw_data_df.drop(columns=["_id"])

            ingested_data_df = ingested_data_df.replace({"na": np.nan})
            logger.info(f"Loaded {len(ingested_data_df)} records from MongoDB.")

            ingested_dir = self.config.ingested_data_dir  # renamed from staging_dir

            create_directories(ingested_dir)
            ingested_data_path = Path(ingested_dir) / self.config.ingested_data_filename
            ingested_data_df.to_csv(ingested_data_path, index=False)
            logger.info(f"Data ingested and saved to dir: '{ingested_data_path.as_posix()}'")

            return ingested_data_df

        except Exception as e:
            logger.error("Failed to load data from MongoDB.")
            raise NetworkSecurityError(e, logger) from e
