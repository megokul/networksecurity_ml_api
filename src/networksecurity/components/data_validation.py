import hashlib
import json
import yaml
import pandas as pd
from pathlib import Path
from scipy.stats import ks_2samp
from box import ConfigBox

from src.networksecurity.entity.config_entity import DataValidationConfig
from src.networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.utils.common import save_to_yaml, save_to_csv, save_to_json


class DataValidation:
    def __init__(self, config: DataValidationConfig, ingestion_artifact: DataIngestionArtifact):
        try:
            self.config = config
            self.schema = config.schema
            self.params = config.validation_params
            self.df = pd.read_csv(ingestion_artifact.ingested_data_filepath)

            self.base_df = None
            self.drift_check_performed = False
            if self.params.drift_detection.enabled and config.validated_dvc_path.exists():
                self.base_df = pd.read_csv(config.validated_dvc_path)
                self.drift_check_performed = True

            self.missing_report_filepath = config.missing_report_filepath
            self.drift_report_filepath = config.drift_report_filepath
            self.validation_report_filepath = config.validation_report_filepath
            self.validated_filepath = None

            self.critical_checks = ConfigBox({
                "schema_is_match": True,
                "no_data_drift": True
            })
            self.non_critical_checks = ConfigBox({
                "no_missing_values": True,
                "no_duplicate_rows": True
            })

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _check_schema_hash(self):
        try:
            expected_schema = self.schema.columns
            expected_str = "|".join(f"{col}:{dtype}" for col, dtype in sorted(expected_schema.items()))
            expected_hash = hashlib.md5(expected_str.encode()).hexdigest()

            current_str = "|".join(f"{col}:{self.df[col].dtype}" for col in sorted(self.df.columns))
            current_hash = hashlib.md5(current_str.encode()).hexdigest()

            if current_hash != expected_hash:
                self.critical_checks.schema_is_match = False
                logger.error("Schema hash mismatch.")
            else:
                logger.info("Schema hash matches schema.yaml.")
        except Exception as e:
            self.critical_checks.schema_is_match = False
            raise NetworkSecurityError(e, logger) from e

    def _check_structure_schema(self):
        try:
            expected = set(self.schema.columns.keys()) | {self.schema.target_column}
            actual = set(self.df.columns)
            if expected != actual:
                self.critical_checks.schema_is_match = False
                logger.error(f"Schema mismatch: expected={expected}, actual={actual}")
        except Exception as e:
            self.critical_checks.schema_is_match = False
            raise NetworkSecurityError(e, logger) from e

    def _check_missing_values(self):
        try:
            missing = self.df.isnull().sum().to_dict()

            save_to_json(missing, self.missing_report_filepath, label="Missing Value")

            if any(v > 0 for v in missing.values()):
                self.non_critical_checks.no_missing_values = False
                logger.warning("Missing values detected.")
            else:
                logger.info("No missing values.")
        except Exception as e:
            self.non_critical_checks.no_missing_values = False
            raise NetworkSecurityError(e, logger) from e

    def _check_duplicates(self):
        try:
            before = len(self.df)
            self.df = self.df.drop_duplicates()
            after = len(self.df)
            duplicates_removed = before - after

            # Prepare report and save it
            duplicate_report = {"duplicate_rows_removed": duplicates_removed}
            save_to_json(duplicate_report, self.config.duplicates_report_filepath, label="Duplicates Report")

            if duplicates_removed > 0:
                self.non_critical_checks.no_duplicate_rows = False
                logger.warning(f"Removed {duplicates_removed} duplicate rows.")
            else:
                logger.info("No duplicate rows found.")

        except Exception as e:
            self.non_critical_checks.no_duplicate_rows = False
            raise NetworkSecurityError(e, logger) from e


    def _check_drift(self):
        try:
            if self.base_df is None:
                logger.info("Base dataset not found. Skipping drift check.")
                return

            drift_results = {}
            drift_detected = False

            for col in self.df.columns:
                if col not in self.base_df.columns:
                    continue
                _, p = ks_2samp(self.base_df[col], self.df[col])
                drift = bool(p < self.params.drift_detection.p_value_threshold)
                drift_results[col] = {"p_value": float(p), "drift": drift}
                if drift:
                    drift_detected = True

            drift_results["drift_detected"] = drift_detected

            save_to_yaml(drift_results, self.config.drift_report_filepath, label="Drift result")

            if drift_detected:
                self.critical_checks.no_data_drift = False
                logger.warning("Data drift detected.")
            else:
                logger.info("No drift detected.")
        except Exception as e:
            self.critical_checks.no_data_drift = False
            raise NetworkSecurityError(e, logger) from e

    def _get_validation_report(self):
        try:
            report = {
                "validation_status": all(self.critical_checks.values()),
                "schema_check_type": self.params.schema_check.method,
                "check_results": {
                    "critical_checks": dict(self.critical_checks),
                    "non_critical_checks": dict(self.non_critical_checks)
                }
            }

            if self.drift_check_performed:
                report["drift_check_method"] = self.params.drift_detection.method
            else:
                report["check_results"]["critical_checks"].pop("no_data_drift", None)

            return report

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def run_validation(self) -> DataValidationArtifact:
        try:
            logger.info("Running data validation...")

            if self.params.schema_check.method == "hash":
                self._check_schema_hash()
            else:
                self._check_structure_schema()

            self._check_missing_values()
            self._check_duplicates()

            if self.params.drift_detection.enabled:
                self._check_drift()

            validation_report = self._get_validation_report()

            save_to_yaml(validation_report, self.validation_report_filepath, label="Validation Report")

            is_valid = all(self.critical_checks.values())

            validated_filepath = None

            if is_valid:

                validated_filepath = self.config.validated_filepath

                save_to_csv(self.df, validated_filepath, self.config.validated_dvc_path, label="Validated Data")
            else:
                logger.warning("Validation failed. Validated data not saved.")

            self.validated_filepath if self.validated_filepath else None,

            return DataValidationArtifact(
                validated_filepath=validated_filepath,
                validation_status=is_valid
            )
        
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e
