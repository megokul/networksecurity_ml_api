from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.components.data_transformation import DataTransformation
from src.networksecurity.entity.artifact_entity import (
    DataValidationArtifact,
    DataTransformationArtifact,
)
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError


class DataTransformationPipeline:
    """
    Orchestrates the Data Transformation stage of the pipeline.

    Responsibilities:
    - Loads transformation configuration
    - Accepts validated artifact
    - Performs feature transformation and returns transformation artifact
    """

    def __init__(self, validation_artifact: DataValidationArtifact):
        try:
            self.config_manager = ConfigurationManager()
            self.config = self.config_manager.get_data_transformation_config()
            self.validation_artifact = validation_artifact
        except Exception as e:
            logger.exception("Failed to initialize DataTransformationPipeline")
            raise NetworkSecurityError(e, logger) from e

    def run(self) -> DataTransformationArtifact:
        try:
            logger.info("========== Data Transformation Stage Started ==========")

            transformer = DataTransformation(
                config=self.config,
                validation_artifact=self.validation_artifact,
            )
            transformation_artifact = transformer.run_transformation()

            logger.info(f"Data Transformation Completed Successfully: {transformation_artifact}")
            logger.info("========== Data Transformation Stage Completed ==========")

            return transformation_artifact

        except Exception as e:
            logger.exception("Data Transformation Stage Failed")
            raise NetworkSecurityError(e, logger) from e
