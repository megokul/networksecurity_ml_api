from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.components.data_validation import DataValidation
from src.networksecurity.entity.artifact_entity import DataIngestionArtifact
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError


class DataValidationPipeline:
    """
    Orchestrates the Data Validation stage of the pipeline.

    Responsibilities:
    - Fetches the configuration and artifacts
    - Loads validated DataFrame from artifact
    - Validates schema and schema hash
    """

    def __init__(self, ingestion_artifact: DataIngestionArtifact):
        try:
            self.config_manager = ConfigurationManager()
            self.ingestion_artifact = ingestion_artifact
            self.config = self.config_manager.get_data_validation_config()
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def run(self):
        try:
            logger.info("========= Data Validation Stage Started =========")
            validation = DataValidation(config=self.config, ingestion_artifact=self.ingestion_artifact)
            validation_artifact = validation.run_validation()
            logger.info(f"Data Validation Completed Successfully: {validation_artifact}")
            logger.info("========= Data Validation Stage Completed =========")
            return validation_artifact
        except Exception as e:
            logger.error("Data Validation Pipeline Failed")
            raise NetworkSecurityError(e, logger) from e
