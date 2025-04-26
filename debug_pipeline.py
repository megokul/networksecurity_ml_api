# FILE: debug_pipeline.py

from dotenv import load_dotenv
from src.networksecurity.pipeline.data_ingestion_pipeline import DataIngestionPipeline
from src.networksecurity.pipeline.data_validation_pipeline import DataValidationPipeline
from src.networksecurity.pipeline.data_transformation_pipeline import DataTransformationPipeline
from src.networksecurity.pipeline.model_trainer_pipeline import ModelTrainerPipeline
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError

# Load environment variables (e.g. MONGO_URI, MLFLOW_TRACKING_URI, etc.)
load_dotenv()

if __name__ == "__main__":
    try:
        # ────────────────
        # Data Ingestion
        # ────────────────
        logger.info("========== Launching Data Ingestion Pipeline ==========")
        ingestion_pipeline = DataIngestionPipeline()
        ingestion_artifact = ingestion_pipeline.run()
        logger.info("========== Data Ingestion Pipeline Finished ==========")
        logger.info("======================================================")

        # ────────────────
        # Data Validation
        # ────────────────
        logger.info("========== Launching Data Validation Pipeline ==========")
        validation_pipeline = DataValidationPipeline(
            ingestion_artifact=ingestion_artifact
        )
        validation_artifact = validation_pipeline.run()
        logger.info("========== Data Validation Pipeline Finished ==========")
        logger.info("======================================================")

        # ────────────────
        # Data Transformation
        # ────────────────
        if validation_artifact.validation_status:
            logger.info("========== Launching Data Transformation Pipeline ==========")
            transformation_pipeline = DataTransformationPipeline(
                validation_artifact=validation_artifact
            )
            transformation_artifact = transformation_pipeline.run()
            logger.info("========== Data Transformation Pipeline Finished ==========")
            logger.info("======================================================")
        else:
            logger.warning("⚠️ Skipping Data Transformation: Validation failed.")
            raise RuntimeError("Cannot proceed to transformation without valid data.")

        # ────────────────
        # Model Training
        # ────────────────
        logger.info("========== Launching Model Trainer Pipeline ==========")
        trainer_pipeline = ModelTrainerPipeline(
            transformation_artifact=transformation_artifact
        )
        trainer_artifact = trainer_pipeline.run()
        logger.info("========== Model Trainer Pipeline Finished ==========")
        logger.info("======================================================")

    except NetworkSecurityError:
        logger.exception("❌ Pipeline failed due to a known exception.")
    except Exception:
        logger.exception("❌ Pipeline failed due to an unexpected exception.")
