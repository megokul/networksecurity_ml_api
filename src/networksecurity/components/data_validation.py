import hashlib
import json
import yaml
import pandas as pd
from pathlib import Path
from scipy.stats import ks_2samp

from src.networksecurity.entity.config_entity import DataValidationConfig
from src.networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.utils.common import create_directories


class DataValidation:
    def __init__(self, config: DataValidationConfig, ingestion_artifact: DataIngestionArtifact):
        try:
            self.config = config
            self.schema = config.schema
            self.params = config.validation_params
            self.df = pd.read_csv(ingestion_artifact.ingested_data_filepath)

            self.base_df = None
            self.drift_check_performed = False
            if self.params.drift_detection.enabled and Path(config.validated_dvc_path).exists():
                self.base_df = pd.read_csv(config.validated_dvc_path)
                self.drift_check_performed = True

            self.missing_report_path = config.missing_report_path
            self.drift_report_path = config.drift_report_path
            self.validation_report_path = config.validation_report_path
            self.validated_output_path = config.validated_filepath

            create_directories(self.validated_output_path.parent)

            self.critical_checks = {
                "schema_is_match": True,
                "no_data_drift": True
            }
            self.non_critical_checks = {
                "no_missing_values": True,
                "no_duplicate_rows": True
            }

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _check_schema_hash(self):
        try:
            expected_schema = self.schema["columns"]
            expected_str = "|".join(f"{col}:{dtype}" for col, dtype in sorted(expected_schema.items()))
            expected_hash = hashlib.md5(expected_str.encode()).hexdigest()

            current_str = "|".join(f"{col}:{self.df[col].dtype}" for col in sorted(self.df.columns))
            current_hash = hashlib.md5(current_str.encode()).hexdigest()

            if current_hash != expected_hash:
                self.critical_checks["schema_is_match"] = False
                logger.error("Schema hash mismatch: dataset columns/types don't match schema.yaml.")
            else:
                logger.info("Schema hash matches schema.yaml.")

        except Exception as e:
            self.critical_checks["schema_is_match"] = False
            raise NetworkSecurityError(e, logger) from e


    def _check_structure_schema(self):
        try:
            expected = set(self.schema["columns"].keys()) | {self.schema["target_column"]}
            actual = set(self.df.columns)
            if expected != actual:
                self.critical_checks["schema_is_match"] = False
                logger.error(f"Schema mismatch: expected={expected}, actual={actual}")
        except Exception as e:
            self.critical_checks["schema_is_match"] = False
            raise NetworkSecurityError(e, logger) from e

    def _check_missing_values(self):
        try:
            missing = self.df.isnull().sum().to_dict()
            with open(self.missing_report_path, "w") as f:
                json.dump(missing, f, indent=4)

            if any(v > 0 for v in missing.values()):
                self.non_critical_checks["no_missing_values"] = False
                logger.warning("Missing values detected.")
            else:
                logger.info("No missing values.")

        except Exception as e:
            self.non_critical_checks["no_missing_values"] = False
            raise NetworkSecurityError(e, logger) from e

    def _check_duplicates(self):
        try:
            before = len(self.df)
            self.df.drop_duplicates(inplace=True)
            after = len(self.df)
            if before != after:
                self.non_critical_checks["no_duplicate_rows"] = False
                logger.warning(f"Removed {before - after} duplicate rows.")
            else:
                logger.info("No duplicate rows found.")
        except Exception as e:
            self.non_critical_checks["no_duplicate_rows"] = False
            raise NetworkSecurityError(e, logger) from e

    def _check_drift(self):
        try:
            if self.base_df is None:
                logger.info("Base dataset not found. Skipping drift check.")
                return

            drift_detected = False
            drift_results = {}

            for col in self.df.columns:
                if col not in self.base_df.columns:
                    continue

                stat, p = ks_2samp(self.base_df[col], self.df[col])
                drift = bool(p < self.params["drift_detection"]["p_value_threshold"])

                drift_results[col] = {
                    "p_value": float(p),
                    "drift": drift
                }

                if drift:
                    drift_detected = True

            drift_results["drift_detected"] = drift_detected

            with open(self.drift_report_path, "w") as f:
                yaml.dump(drift_results, f, default_flow_style=False, sort_keys=False)

            if drift_detected:
                self.critical_checks["no_data_drift"] = False
                logger.warning("Data drift detected.")
            else:
                logger.info("No drift detected.")

        except Exception as e:
            self.critical_checks["no_data_drift"] = False
            raise NetworkSecurityError(e, logger) from e

    def _save_validation_report(self):
        try:
            report = {
                "validation_status": all(self.critical_checks.values()),
                "schema_check_type": self.params["schema_check"]["method"],
                "check_results": {
                    "critical_checks": self.critical_checks,
                    "non_critical_checks": self.non_critical_checks,
                },
            }

            if self.drift_check_performed:
                report["drift_check_method"] = self.params["drift_detection"]["method"]
            else:
                report["check_results"]["critical_checks"].pop("no_data_drift", None)

            with open(self.validation_report_path, "w") as f:
                yaml.dump(report, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Validation report saved to: {self.validation_report_path}")
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def run_validation(self) -> DataValidationArtifact:
        try:
            logger.info("Running data validation...")

            if self.params["schema_check"]["method"] == "hash":
                self._check_schema_hash()
            else:
                self._check_structure_schema()

            self._check_missing_values()
            self._check_duplicates()

            if self.params["drift_detection"]["enabled"]:
                self._check_drift()

            self._save_validation_report()

            is_valid = all(self.critical_checks.values())
            validated_path = None

            if is_valid:
                self.df.to_csv(self.validated_output_path, index=False)
                logger.info(f"Validated data saved to: {self.validated_output_path}")

                final_validated_path = self.config.validated_dvc_path
                final_validated_path.parent.mkdir(parents=True, exist_ok=True)
                self.df.to_csv(final_validated_path, index=False)
                logger.info(f"Validated data copied to: {final_validated_path}")

                validated_path = self.validated_output_path
            else:
                logger.warning("Validation failed. Validated data not saved.")

            return DataValidationArtifact(
                validated_path=validated_path,
                drift_report_path=self.drift_report_path,
                validation_status=is_valid
            )

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e
