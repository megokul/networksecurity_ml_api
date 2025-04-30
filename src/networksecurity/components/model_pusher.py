from src.networksecurity.entity.config_entity import ModelPusherConfig
from src.networksecurity.entity.artifact_entity import ModelTrainerArtifact, ModelPusherArtifact
from src.networksecurity.cloud.s3_syncer import S3Syncer
from src.networksecurity.utils.core import save_object
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


class ModelPusher:
    """
    Pushes the final trained model to local storage and optionally to S3.
    """

    def __init__(self, model_pusher_config: ModelPusherConfig, model_trainer_artifact: ModelTrainerArtifact) -> None:
        try:
            self.config = model_pusher_config
            self.trainer_artifact = model_trainer_artifact
        except Exception as e:
            logger.exception("Failed to initialize ModelPusher")
            raise NetworkSecurityError(e, logger) from e

    def push_model(self) -> ModelPusherArtifact:
        try:
            logger.info("Starting model push process...")

            # Save model locally
            save_object(
                obj=self.trainer_artifact.trained_model_filepath,
                path=self.config.pushed_model_filepath,
                label="Final Model"
            )

            # Sync to S3
            s3_syncer = S3Syncer(bucket_name=self.config.final_model_s3_bucket)
            s3_syncer.upload_file(
                local_path=self.config.pushed_model_filepath,
                s3_key=self.config.final_model_local_path.name  # S3 key = filename only
            )

            logger.info("Model push process completed successfully.")
            return ModelPusherArtifact(
                pushed_model_local_path=self.config.pushed_model_filepath,
                pushed_model_s3_path=f"s3://{self.config.final_model_s3_bucket}/{self.config.final_model_local_path.name}"
            )

        except Exception as e:
            logger.exception("Model push failed")
            raise NetworkSecurityError(e, logger) from e
