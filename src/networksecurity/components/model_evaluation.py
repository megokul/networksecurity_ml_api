from pathlib import Path
from typing import Dict
import numpy as np

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from src.networksecurity.entity.config_entity import ModelEvaluationConfig
from src.networksecurity.entity.artifact_entity import ModelEvaluationArtifact, ModelTrainerArtifact
from src.networksecurity.utils.core import load_object, load_array, save_to_yaml
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.inference.estimator import NetworkModel


class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig, trainer_artifact: ModelTrainerArtifact):
        try:
            self.config = config
            self.trainer_artifact = trainer_artifact

            logger.info(f"Initializing ModelEvaluator with root_dir={config.root_dir}")
            self.config.root_dir.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _load_data(self):
        try:
            self.X_train = load_array(self.trainer_artifact.x_train_filepath, label="X Train")
            self.y_train = load_array(self.trainer_artifact.y_train_filepath, label="Y Train")
            self.X_val = load_array(self.trainer_artifact.x_val_filepath, label="X Val")
            self.y_val = load_array(self.trainer_artifact.y_val_filepath, label="Y Val")
            self.X_test = load_array(self.trainer_artifact.x_test_filepath, label="X Test")
            self.y_test = load_array(self.trainer_artifact.y_test_filepath, label="Y Test")

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _load_model(self):
        try:
            self.model: NetworkModel = load_object(self.trainer_artifact.trained_model_filepath)
            logger.info(f"Inference Model loaded successfully for evaluation.")
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _evaluate_split(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        try:
            y_pred = self.model.predict(X)

            metrics = {
                "accuracy": accuracy_score(y_true, y_pred),
                "f1": f1_score(y_true, y_pred),
                "precision": precision_score(y_true, y_pred),
                "recall": recall_score(y_true, y_pred),
            }
            return metrics

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def run_evaluation(self) -> ModelEvaluationArtifact:
        try:
            logger.info("========== Starting Model Evaluation ==========")

            self._load_data()
            self._load_model()

            evaluation_report = {
                "train_metrics": self._evaluate_split(self.X_train, self.y_train),
                "val_metrics": self._evaluate_split(self.X_val, self.y_val),
                "test_metrics": self._evaluate_split(self.X_test, self.y_test),
            }

            save_to_yaml(
                evaluation_report,
                self.config.evaluation_report_filepath,
                label="Evaluation Report"
            )

            logger.info("========== Model Evaluation Completed ==========")

            return ModelEvaluationArtifact(
                evaluation_report_filepath=self.config.evaluation_report_filepath
            )

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e
