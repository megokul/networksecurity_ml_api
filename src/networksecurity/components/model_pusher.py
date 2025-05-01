from src.networksecurity.entity.config_entity import ModelPusherConfig
from src.networksecurity.entity.artifact_entity import ModelTrainerArtifact, ModelPusherArtifact
from src.networksecurity.cloud.s3_syncer import S3Syncer
from src.networksecurity.utils.core import save_object, load_object
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from pathlib import Path


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

            final_model = load_object(self.trainer_artifact.trained_model_filepath)

            # Save model locally
            save_object(
                obj=final_model,
                path=self.config.pushed_model_filepath,
                label="Final Model"
            )

            s3_syncer = S3Syncer(
                bucket_name=self.config.final_model_s3_bucket,
                region=self.config.aws_region
            )

            if self.config.upload_to_s3:
                # Upload only the final model file
                s3_syncer.upload_file(
                    local_path=self.config.pushed_model_filepath,
                    s3_key=self.config.s3_key_final_model,
                )

                # Upload entire artifacts folder
                s3_syncer.sync_directory(
                    local_dir=Path("artifacts"),
                    s3_prefix=f"{self.config.s3_artifacts_folder}/artifacts"
                )

                # Upload entire logs folder
                s3_syncer.sync_directory(
                    local_dir=Path("logs"),
                    s3_prefix=f"{self.config.s3_artifacts_folder}/logs"
                )

            logger.info("Model push process completed successfully.")
            return ModelPusherArtifact(
                pushed_model_local_path=self.config.pushed_model_filepath,
                pushed_model_s3_path=f"s3://{self.config.final_model_s3_bucket}/{self.config.s3_key_final_model}",
            )

        except Exception as e:
            logger.exception("Model push failed")
            raise NetworkSecurityError(e, logger) from e

