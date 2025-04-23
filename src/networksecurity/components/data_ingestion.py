import numpy as np
import pandas as pd

from src.networksecurity.entity.config_entity import DataIngestionConfig
from src.networksecurity.entity.artifact_entity import DataIngestionArtifact
from src.networksecurity.dbhandler.base_handler import DBHandler
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.utils.core import save_to_csv, read_csv


class DataIngestion:
    def __init__(
        self,
        config: DataIngestionConfig,
        db_handler: DBHandler,
    ):
        try:
            self.config = config
            self.db_handler = db_handler
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def __fetch_raw_data(self) -> pd.DataFrame:
        try:
            with self.db_handler as handler:
                df = handler.load_from_source()
            logger.info(f"Fetched {len(df)} raw rows from data source.")
            return df
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def __clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df_cleaned = df.drop(columns=["_id"], errors="ignore").copy()
            df_cleaned.replace({"na": np.nan}, inplace=True)
            logger.info("Raw DataFrame cleaned successfully.")
            return df_cleaned
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def run_ingestion(self) -> DataIngestionArtifact:
        try:
            logger.info("========== Starting Data Ingestion ==========")

            # Step 1: Fetch raw data
            raw_df = self.__fetch_raw_data()

            # Step 2: Save raw data
            save_to_csv(
                raw_df,
                self.config.raw_data_filepath,
                self.config.raw_dvc_path,
                label="Raw Data"
            )

            # Step 3: Clean raw data
            cleaned_df = self.__clean_dataframe(raw_df)

            # Step 4: Save cleaned (ingested) data
            save_to_csv(
                cleaned_df,
                self.config.ingested_data_filepath,
                label="Cleaned (Ingested) Data"
            )

            logger.info("========== Data Ingestion Completed ==========")

            return DataIngestionArtifact(
                raw_artifact_path=self.config.raw_data_filepath,
                raw_dvc_path=self.config.raw_dvc_path,
                ingested_data_filepath=self.config.ingested_data_filepath,
            )

        except Exception as e:
            logger.error("Data ingestion failed.")
            raise NetworkSecurityError(e, logger) from e
