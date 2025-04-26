from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.components.model_trainer import ModelTrainer
from src.networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError


class ModelTrainerPipeline:
    """
    Orchestrates the Model Training stage of the pipeline.

    Responsibilities:
    - Loads model‐trainer configuration
    - Accepts transformation artifact
    - Trains (and tunes) candidate models
    - Logs & registers via MLflow
    - Emits a ModelTrainerArtifact
    """

    def __init__(self, transformation_artifact: DataTransformationArtifact):
        try:
            self.config_manager = ConfigurationManager()
            self.config = self.config_manager.get_model_trainer_config()
            self.transformation_artifact = transformation_artifact
        except Exception as e:
            logger.exception("Failed to initialize ModelTrainerPipeline")
            raise NetworkSecurityError(e, logger) from e

    def run(self) -> ModelTrainerArtifact:
        try:
            logger.info("========== Model Training Stage Started ==========")

            trainer = ModelTrainer(
                config=self.config,
                transformation_artifact=self.transformation_artifact
            )
            trainer_artifact = trainer.run_training()

            logger.info(f"Model Training Completed Successfully: {trainer_artifact}")
            logger.info("========== Model Training Stage Completed ==========")

            return trainer_artifact

        except Exception as e:
            logger.exception("Model Training Stage Failed")
            raise NetworkSecurityError(e, logger) from e
