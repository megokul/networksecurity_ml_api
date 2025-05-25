from src.networksecurity.pipeline.training_pipeline import TrainingPipeline
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger

if __name__ == "__main__":
    try:
        logger.info("========== Pipeline Execution Started from main.py ==========")

        pipeline = TrainingPipeline()
        result = pipeline.run_pipeline()

        logger.info(f"Pipeline execution completed successfully.\n{result}")
        logger.info("========== Pipeline Execution Completed from main.py ==========")

    except NetworkSecurityError as nse:
        logger.error(f"Pipeline failed due to custom error: {nse}")
    except Exception as e:
        logger.exception(f"Unexpected error in main.py: {e}")
