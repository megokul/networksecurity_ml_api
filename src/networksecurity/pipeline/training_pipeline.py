import sys

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger

from src.networksecurity.components.data_ingestion import DataIngestion
from src.networksecurity.components.data_validation import DataValidation
from src.networksecurity.components.data_transformation import DataTransformation
from src.networksecurity.components.model_trainer import ModelTrainer
from src.networksecurity.components.model_evaluation import ModelEvaluation
from src.networksecurity.components.model_pusher import ModelPusher

from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.dbhandler.mongodb_handler import MongoDBHandler
from src.networksecurity.dbhandler.s3_handler import S3Handler

from src.networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
    ModelEvaluationArtifact,
    ModelPusherArtifact,
)


class TrainingPipeline:
    """
    Orchestrates the full end-to-end training pipeline:
    - MongoDB ingestion
    - Validation
    - Transformation
    - Training
    - Evaluation
    - Model push (local + optional S3)
    """

    def __init__(self) -> None:
        try:
            self.config_manager = ConfigurationManager()
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def run_pipeline(self) -> ModelPusherArtifact:
        try:
            logger.info("========== Training Pipeline Started ==========")

            # ───────────────
            # MongoDB Handler
            # ───────────────
            mongo_config = self.config_manager.get_mongo_handler_config()
            mongo_handler = MongoDBHandler(config=mongo_config)

            # ───────────────
            # Data Ingestion
            # ───────────────
            ingestion_config = self.config_manager.get_data_ingestion_config()
            ingestion = DataIngestion(config=ingestion_config, db_handler=mongo_handler)
            ingestion_artifact: DataIngestionArtifact = ingestion.run_ingestion()

            # ───────────────
            # Data Validation
            # ───────────────
            validation_config = self.config_manager.get_data_validation_config()
            validation = DataValidation(config=validation_config, ingestion_artifact=ingestion_artifact)
            validation_artifact: DataValidationArtifact = validation.run_validation()

            if not validation_artifact.validation_status:
                logger.error("Validation failed. Aborting pipeline.")
                raise RuntimeError("Data validation failed. Pipeline terminated.")

            # ──────────────────
            # Data Transformation
            # ──────────────────
            transformation_config = self.config_manager.get_data_transformation_config()
            transformation = DataTransformation(config=transformation_config, validation_artifact=validation_artifact)
            transformation_artifact: DataTransformationArtifact = transformation.run_transformation()

            # ───────────────
            # Model Training
            # ───────────────
            trainer_config = self.config_manager.get_model_trainer_config()
            trainer = ModelTrainer(config=trainer_config, transformation_artifact=transformation_artifact)
            trainer_artifact: ModelTrainerArtifact = trainer.run_training()

            # ────────────────
            # Model Evaluation
            # ────────────────
            evaluation_config = self.config_manager.get_model_evaluation_config()
            evaluator = ModelEvaluation(config=evaluation_config, trainer_artifact=trainer_artifact)
            evaluation_artifact: ModelEvaluationArtifact = evaluator.run_evaluation()

            # ───────────────
            # Model Pusher
            # ───────────────
            pusher_config = self.config_manager.get_model_pusher_config()
            s3_handler_config = self.config_manager.get_s3_handler_config()
            s3_handler = S3Handler(config=s3_handler_config)

            pusher = ModelPusher(
                model_pusher_config=pusher_config,
                s3_handler=s3_handler,
                model_trainer_artifact=trainer_artifact
            )
            pusher_artifact: ModelPusherArtifact = pusher.push_model()

            logger.info("========== Training Pipeline Completed Successfully ==========")
            return pusher_artifact

        except Exception as e:
            logger.exception("Training Pipeline Failed")
            raise NetworkSecurityError(e, logger) from e
