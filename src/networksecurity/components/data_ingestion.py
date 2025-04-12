

from src.networksecurity.entity.config_entity import DataIngestionConfig, MongoDBConfig
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

            logger.info(f"Reading data from MongoDB: {database_name}/{collection_name}")
            ingested_df = pd.DataFrame(list(collection.find()))

            if "_id" in ingested_df.columns:
                ingested_df.drop(columns=["_id"], inplace=True)

            ingested_df = ingested_df.replace({"na": np.nan})
            logger.info(f"Loaded {len(ingested_df)} records from MongoDB.")

            # Prepare staging path
            staging_dir = Path(self.config.staging_data_dir)
            csv_path = staging_dir / self.config.ingested_data_filename

            create_directories(staging_dir)
            ingested_df.to_csv(csv_path, index=False)
            logger.info(f"Data saved to: {csv_path.as_posix()}")  # Apply as_posix only for logging

            return ingested_df

        except Exception as e:
            logger.error("Failed to load data from MongoDB.")
            raise NetworkSecurityError(e, logger) from e
