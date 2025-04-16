from src.networksecurity.entity.config_entity import DataIngestionConfig, MongoHandlerConfig
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.dbhandler.mongo_handler import MongoDBHandler
from src.networksecurity.utils.common import create_directories

import pandas as pd
import numpy as np


class DataIngestion:
    def __init__(self, ingestion_config: DataIngestionConfig, mongo_config: MongoHandlerConfig):
        """
        Initializes the DataIngestion process with configuration for both
        data paths and MongoDB connection.

        Args:
            ingestion_config (DataIngestionConfig): Config for file paths and storage.
            mongo_config (MongoHandlerConfig): Config for MongoDB connection and access.
        """
        try:
            self.ingestion_config = ingestion_config
            self.mongo_config = mongo_config
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def load_data_from_mongo(self) -> pd.DataFrame:
        """
        Connects to MongoDB, exports data, saves raw and cleaned CSVs.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        try:
            logger.info("Starting data ingestion from MongoDB.")

            # Step 1: Fetch data from MongoDB
            mongo_handler = MongoDBHandler(config=self.mongo_config)
            raw_df = mongo_handler.export_collection_as_dataframe()

            # Step 2: Save raw data
            create_directories(self.ingestion_config.featurestore_dir)
            raw_df.to_csv(self.ingestion_config.raw_data_filepath, index=False)
            logger.info(f"Raw data saved to: {self.ingestion_config.raw_data_filepath.as_posix()}")

            # Step 3: Clean data
            cleaned_df = raw_df.drop(columns=["_id"]) if "_id" in raw_df.columns else raw_df.copy()
            cleaned_df.replace({"na": np.nan}, inplace=True)

            # Step 4: Save cleaned data
            create_directories(self.ingestion_config.ingested_data_dir)
            cleaned_df.to_csv(self.ingestion_config.ingested_data_filepath, index=False)
            logger.info(f"Cleaned data saved to: {self.ingestion_config.ingested_data_filepath.as_posix()}")

            logger.info(f"Data ingestion complete. {len(cleaned_df)} rows ingested.")
            return cleaned_df

        except Exception as e:
            logger.error("Error occurred during data ingestion.")
            raise NetworkSecurityError(e, logger) from e
