# FILE: debug_pipeline.py

import sys
from src.networksecurity.pipeline.training_pipeline import TrainingPipeline
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


def run_debug_pipeline() -> None:
    """
    Trigger the full training pipeline in debug mode.
    Logs structured output and final artifact summary.
    """
    try:
        logger.info("\n DEBUG MODE: Starting the Training Pipeline...\n")

        pipeline = TrainingPipeline()
        final_artifact = pipeline.run_pipeline()

        logger.info("\n Final ModelPusherArtifact:")
        logger.info(final_artifact)

    except NetworkSecurityError as nse:
        logger.error("Training pipeline failed with a NetworkSecurityError.")
        logger.error(nse)

    except Exception as e:
        logger.exception("Unexpected error occurred during pipeline execution.")
        sys.exit(1)


if __name__ == "__main__":
    run_debug_pipeline()
