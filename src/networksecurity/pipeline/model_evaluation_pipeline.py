from src.networksecurity.config.configuration import ConfigurationManager
from src.networksecurity.components.model_evaluation import ModelEvaluation
from src.networksecurity.entity.artifact_entity import (
    ModelTrainerArtifact,
    ModelEvaluationArtifact,
)
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError

class ModelEvaluationPipeline:
    """
    Orchestrates the Model Evaluation stage of the pipeline.

    Responsibilities:
    - Loads model evaluation configuration
    - Accepts only the trainer artifact (no transformation artifact needed)
    - Evaluates trained model on train/val/test datasets
    - Emits a ModelEvaluationArtifact
    """

    def __init__(self, trainer_artifact: ModelTrainerArtifact):
        try:
            logger.info("Initializing ModelEvaluationPipeline...")
            self.config = ConfigurationManager().get_model_evaluation_config()
            self.trainer_artifact = trainer_artifact
        except Exception as e:
            logger.exception("Failed to initialize ModelEvaluationPipeline")
            raise NetworkSecurityError(e, logger) from e

    def run(self) -> ModelEvaluationArtifact:
        try:
            logger.info("========== Model Evaluation Stage Started ==========")

            evaluator = ModelEvaluation(
                config=self.config,
                trainer_artifact=self.trainer_artifact
            )
            evaluation_artifact = evaluator.run_evaluation()

            logger.info(f"Model Evaluation Completed Successfully: {evaluation_artifact}")
            logger.info("========== Model Evaluation Stage Completed ==========")

            return evaluation_artifact

        except Exception as e:
            logger.exception("Model Evaluation Stage Failed")
            raise NetworkSecurityError(e, logger) from e
