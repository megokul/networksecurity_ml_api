import numpy as np

from src.networksecurity.entity.config_entity import DataIngestionConfig
from src.networksecurity.entity.artifact_entity import DataIngestionArtifact
from src.networksecurity.dbhandler.mongo_handler import MongoDBHandler
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.utils.common import create_directories


class DataIngestion:
    def __init__(
        self,
        config: DataIngestionConfig,
        mongo_handler: MongoDBHandler,
    ):
        """
        Data ingestion stage responsible for fetching raw data from MongoDB,
        saving to artifact and DVC directories, and preparing cleaned versions.

        Args:
            config (DataIngestionConfig): Config paths for saving outputs.
            mongo_handler (MongoDBHandler): Handler capable of exporting data from MongoDB.
        """
        try:
            self.config = config
            self.mongo_handler = mongo_handler
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def load_data_from_mongo(self) -> DataIngestionArtifact:
        """
        Fetch data from MongoDB, save both raw and cleaned versions
        to artifact and DVC paths, and return ingestion artifacts.

        Returns:
            DataIngestionArtifact: Paths to all raw and cleaned data outputs.
        """
        try:
            logger.info("Starting data ingestion from MongoDB.")

            with self.mongo_handler as handler:
                raw_df = handler.export_collection_as_dataframe()
            logger.info(f"Fetched {len(raw_df)} raw rows from MongoDB.")

            # Save raw data to both artifact and DVC
            create_directories(self.config.raw_dvc_path.parent)
            raw_df.to_csv(self.config.raw_data_filepath, index=False)
            raw_df.to_csv(self.config.raw_dvc_path, index=False)

            # Clean
            cleaned_df = raw_df.drop(columns=["_id"], errors="ignore").copy()
            cleaned_df.replace({"na": np.nan}, inplace=True)

            # Save cleaned to both artifact and DVC
            create_directories(self.config.processed_dvc_path.parent)
            cleaned_df.to_csv(self.config.ingested_data_filepath, index=False)
            cleaned_df.to_csv(self.config.processed_dvc_path, index=False)

            logger.info("Data ingestion completed successfully.")

            return DataIngestionArtifact(
                raw_artifact_path=self.config.raw_data_filepath,
                cleaned_artifact_path=self.config.ingested_data_filepath,
                raw_dvc_path=self.config.raw_dvc_path,
                cleaned_dvc_path=self.config.processed_dvc_path,
            )

        except Exception as e:
            logger.error("Data ingestion failed.")
            raise NetworkSecurityError(e, logger) from e
