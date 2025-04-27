from pathlib import Path
from datetime import datetime, timezone
import os
import importlib
import numpy as np
import optuna
import mlflow
import dagshub
import joblib
from sklearn.model_selection import cross_val_score
from sklearn.metrics import get_scorer
from mlflow import sklearn as mlflow_sklearn

from src.networksecurity.entity.config_entity import ModelTrainerConfig
from src.networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.utils.core import save_to_yaml, save_object, load_array
from src.networksecurity.inference.estimator import NetworkModel


class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig, transformation_artifact: DataTransformationArtifact):
        try:
            self.config = config
            self.transformation_artifact = transformation_artifact
            logger.info(f"Initializing ModelTrainer with root_dir={config.root_dir}")
            config.root_dir.mkdir(parents=True, exist_ok=True)

            if config.tracking.mlflow.enabled:
                dagshub.init(
                    repo_owner=os.getenv("DAGSHUB_REPO_OWNER"),
                    repo_name=os.getenv("DAGSHUB_REPO_NAME"),
                    mlflow=True,
                )
                mlflow.set_tracking_uri(config.tracking.tracking_uri)
                mlflow.set_experiment(config.tracking.mlflow.experiment_name)
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _load_data(self):
        try:
            self.X_train = load_array(self.transformation_artifact.x_train_filepath, "X train")
            self.y_train = load_array(self.transformation_artifact.y_train_filepath, "Y train")
            self.X_val = load_array(self.transformation_artifact.x_val_filepath, "X val")
            self.y_val = load_array(self.transformation_artifact.y_val_filepath, "Y val")
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _instantiate(self, full_class_string: str, params: dict):
        module_path, class_name = full_class_string.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)(**(params or {}))

    def _optimize_one(self, model_spec: dict):
        model_name = model_spec["name"]
        search_space = model_spec.get("search_space", {})

        def objective(trial):
            sampled = {}
            for name, space in search_space.items():
                if "choices" in space:
                    sampled[name] = trial.suggest_categorical(name, space["choices"])
                else:
                    low, high = space["low"], space["high"]
                    step = space.get("step", 1)
                    log = space.get("log", False)
                    if isinstance(low, int) and isinstance(high, int):
                        sampled[name] = trial.suggest_int(name, low, high, step=step)
                    else:
                        sampled[name] = trial.suggest_float(name, float(low), float(high), log=log)
            clf = self._instantiate(model_name, sampled)
            scores = cross_val_score(clf, self.X_train, self.y_train, cv=self.config.optimization.cv_folds,
                                     scoring=self.config.optimization.scoring, n_jobs=-1)
            return scores.mean()

        study = optuna.create_study(direction=self.config.optimization.direction)
        study.optimize(objective, n_trials=self.config.optimization.n_trials)
        return study.best_trial, study

    def _select_and_tune(self):
        best_result = {"score": -np.inf, "spec": None, "trial": None, "study": None}

        for model_spec in self.config.models:
            if self.config.optimization.enabled:
                trial, study = self._optimize_one(model_spec)
                score = trial.value
            else:
                model = self._instantiate(model_spec["name"], model_spec.get("params", {}))
                score = cross_val_score(model, self.X_train, self.y_train, cv=self.config.optimization.cv_folds,
                                        scoring=self.config.optimization.scoring).mean()
                trial, study = None, None

            if score > best_result["score"]:
                best_result.update(score=score, spec=model_spec, trial=trial, study=study)

        return best_result

    def _train_and_eval(self, model_spec: dict, params: dict):
        clf = self._instantiate(model_spec["name"], params)
        clf.fit(self.X_train, self.y_train)

        train_metrics = {m: get_scorer(m)(clf, self.X_train, self.y_train)
                         for m in self.config.tracking.mlflow.metrics_to_log}
        val_metrics = {m: get_scorer(m)(clf, self.X_val, self.y_val)
                       for m in self.config.tracking.mlflow.metrics_to_log}
        return clf, train_metrics, val_metrics

    def _generate_report(self, best, train_metrics, val_metrics):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "best_model": best["spec"]["name"].split(".")[-1],
            "best_model_params": best["trial"].params if best["trial"] else best["spec"].get("params", {}),
            "train_metrics": train_metrics,
            "val_metrics": val_metrics,
            "optimization": {
                "enabled": self.config.optimization.enabled,
                "best_trial": best["trial"].number if best["trial"] else None,
                "cv_folds": self.config.optimization.cv_folds,
                "direction": self.config.optimization.direction,
                "mean_score": best["score"]
            }
        }

    def run_training(self) -> ModelTrainerArtifact:
        try:
            logger.info("========== Starting Model Training ==========")
            self._load_data()

            with mlflow.start_run():
                best = self._select_and_tune()
                params = best["trial"].params if best["trial"] else best["spec"].get("params", {})
                model, train_m, val_m = self._train_and_eval(best["spec"], params)

                mlflow.log_params(params)
                for k, v in train_m.items():
                    mlflow.log_metric(f"train_{k}", v)
                for k, v in val_m.items():
                    mlflow.log_metric(f"val_{k}", v)

                # Save raw trained model
                trained_model_dir = self.config.root_dir / "trained_model"
                trained_model_path = trained_model_dir / "model.joblib"
                save_object(model, trained_model_path, "Trained Model")

                # Save inference-ready model (NetworkModel)
                network_model = NetworkModel.from_objects(
                    model=model,
                    x_preprocessor=joblib.load(self.transformation_artifact.x_preprocessor_filepath),
                    y_preprocessor=joblib.load(self.transformation_artifact.y_preprocessor_filepath),
                )
                inference_model_dir = self.config.root_dir / "inference_model"
                inference_model_path = inference_model_dir / "inference_model.joblib"
                save_object(network_model, inference_model_path, "Inference Model")

                # Save training report
                report_dir = self.config.root_dir / "reports"
                report_path = report_dir / "training_report.yaml"
                save_to_yaml(self._generate_report(best, train_m, val_m), report_path, label="Training Report")

            logger.info("========== Model Training Completed ==========")
            return ModelTrainerArtifact(
                trained_model_filepath=inference_model_path,
                training_report_filepath=report_path,
            )

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e
