from src.networksecurity.entity.config_entity import ModelPusherConfig
from src.networksecurity.entity.artifact_entity import ModelTrainerArtifact, ModelPusherArtifact
from src.networksecurity.dbhandler.s3_handler import S3Handler
from src.networksecurity.utils.core import save_object, load_object
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from pathlib import Path


class ModelPusher:
    """
    Pushes the final trained model to local storage and optionally to S3.
    """

    def __init__(
        self,
        model_pusher_config: ModelPusherConfig,
        model_trainer_artifact: ModelTrainerArtifact,
        s3_handler: S3Handler,
    ) -> None:
        try:
            self.config = model_pusher_config
            self.trainer_artifact = model_trainer_artifact
            self.s3_handler = s3_handler
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
                label="Final Model",
            )

            if self.config.upload_to_s3:
                with self.s3_handler as handler:

                    s3_key_final_model = handler.config.s3_final_model_prefix + "/" + self.config.pushed_model_filename

                    # Upload only the final model file
                    handler.upload_file(
                        local_path=self.config.pushed_model_filepath,
                        s3_key=s3_key_final_model,
                    )

                    s3_key_artifacts = handler.config.s3_artifacts_prefix + "/artifacts"

                    # Upload entire artifacts folder
                    handler.sync_directory(
                        local_dir=Path("artifacts"),
                        s3_prefix=s3_key_artifacts,
                    )

                    # Upload entire logs folder
                    handler.sync_directory(
                        local_dir=Path("logs"),
                        s3_prefix=handler.config.s3_artifacts_prefix + "/logs"
                    )

            logger.info("Model push process completed successfully.")
            return ModelPusherArtifact(
                pushed_model_local_path=self.config.pushed_model_filepath,
                pushed_model_s3_path=f"s3://{self.s3_handler.config.bucket_name}/{s3_key_final_model}",
            )

        except Exception as e:
            logger.exception("Model push failed")
            raise NetworkSecurityError(e, logger) from e
