from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.components.model_pusher import ModelPusher
from src.networksecurity.entity.artifact_entity import ModelTrainerArtifact, ModelPusherArtifact
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


class ModelPusherPipeline:
    """
    Orchestrates the model pushing stage.

    Responsibilities:
    - Loads model pusher configuration
    - Accepts the ModelTrainerArtifact
    - Saves final model to local path
    - Pushes model to S3 via S3Syncer
    - Emits a ModelPusherArtifact
    """

    def __init__(self, model_trainer_artifact: ModelTrainerArtifact) -> None:
        try:
            logger.info("Initializing ModelPusherPipeline...")

            self.config = ConfigurationManager().get_model_pusher_config()
            self.model_trainer_artifact = model_trainer_artifact

        except Exception as e:
            logger.exception("Failed to initialize ModelPusherPipeline")
            raise NetworkSecurityError(e, logger) from e

    def run(self) -> ModelPusherArtifact:
        try:
            logger.info("========== Model Pusher Stage Started ==========")

            model_pusher = ModelPusher(
                model_pusher_config=self.config,
                model_trainer_artifact=self.model_trainer_artifact
            )
            pusher_artifact = model_pusher.push_model()

            logger.info(f"Model Pusher Stage Completed Successfully: {pusher_artifact}")
            logger.info("========== Model Pusher Stage Completed ==========")

            return pusher_artifact

        except Exception as e:
            logger.exception("Model Pusher Stage Failed")
            raise NetworkSecurityError(e, logger) from e
