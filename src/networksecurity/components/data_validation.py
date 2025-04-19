import hashlib
import pandas as pd
from pathlib import Path
from box import ConfigBox
from datetime import timezone
from scipy.stats import ks_2samp

from src.networksecurity.entity.config_entity import DataValidationConfig
from src.networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.utils.common import save_to_yaml, save_to_csv, save_to_json, read_csv
from src.networksecurity.utils.timestamp import get_shared_utc_timestamp


class DataValidation:
    def __init__(self, config: DataValidationConfig, ingestion_artifact: DataIngestionArtifact):
        try:
            self.config = config
            self.schema = config.schema
            self.params = config.validation_params
            self.df = read_csv(ingestion_artifact.ingested_data_filepath, "Ingested Data")

            self.base_df = None
            self.drift_check_performed = False
            if self.params.drift_detection.enabled and config.validated_dvc_path.exists():
                self.base_df = read_csv(config.validated_dvc_path, "Validated Base Data")
                self.drift_check_performed = True

            self.validated_filepath = None
            self.timestamp = get_shared_utc_timestamp()

            self.report = ConfigBox(config.val_report_template.copy())
            self.critical_checks = ConfigBox({k: False for k in self.report.check_results.critical_checks.keys()})
            self.non_critical_checks = ConfigBox({k: False for k in self.report.check_results.non_critical_checks.keys()})
        except Exception as e:
            raise NetworkSecurityError(e, logger) from e

    def _check_schema_hash(self):
        try:
            expected_schema = self.schema.columns
            expected_str = "|".join(f"{col}:{dtype}" for col, dtype in sorted(expected_schema.items()))
            expected_hash = hashlib.md5(expected_str.encode()).hexdigest()

            current_str = "|".join(f"{col}:{self.df[col].dtype}" for col in sorted(self.df.columns))
            current_hash = hashlib.md5(current_str.encode()).hexdigest()

            self.critical_checks.schema_is_match = (current_hash == expected_hash)
            logger.info("Schema hash check passed." if self.critical_checks.schema_is_match else "Schema hash mismatch.")
        except Exception as e:
            self.critical_checks.schema_is_match = False
            raise NetworkSecurityError(e, logger) from e

    def _check_structure_schema(self):
        try:
            expected = set(self.schema.columns.keys()) | {self.schema.target_column}
            actual = set(self.df.columns)
            self.critical_checks.schema_is_match = (expected == actual)
            if not self.critical_checks.schema_is_match:
                logger.error(f"Schema structure mismatch: expected={expected}, actual={actual}")
        except Exception as e:
            self.critical_checks.schema_is_match = False
            raise NetworkSecurityError(e, logger) from e

    def _check_missing_values(self):
        try:
            missing = self.df.isnull().sum().to_dict()
            missing["timestamp"] = self.timestamp
            save_to_yaml(missing, self.config.missing_report_filepath, label="Missing Value Report")
            self.non_critical_checks.no_missing_values = not any(v > 0 for v in missing.values() if isinstance(v, (int, float)))
        except Exception as e:
            self.non_critical_checks.no_missing_values = False
            raise NetworkSecurityError(e, logger) from e

    def _check_duplicates(self):
        try:
            before = len(self.df)
            self.df = self.df.drop_duplicates()
            after = len(self.df)
            duplicates_removed = before - after

            result = {
                "duplicate_rows_removed": duplicates_removed,
                "timestamp": self.timestamp
            }

            save_to_json(result, self.config.duplicates_report_filepath, label="Duplicates Report")
            self.non_critical_checks.no_duplicate_rows = (duplicates_removed == 0)
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
            drift_results["timestamp"] = self.timestamp

            save_to_yaml(drift_results, self.config.drift_report_filepath, label="Drift Result")
            self.critical_checks.no_data_drift = not drift_detected
        except Exception as e:
            self.critical_checks.no_data_drift = False
            raise NetworkSecurityError(e, logger) from e

    def _generate_report(self) -> dict:
        try:
            validation_status = all(self.critical_checks.values())
            non_critical_passed = all(self.non_critical_checks.values())

            self.report.timestamp = self.timestamp
            self.report.validation_status = validation_status
            self.report.critical_passed = validation_status
            self.report.non_critical_passed = non_critical_passed
            self.report.schema_check_type = self.params.schema_check.method

            if self.drift_check_performed:
                self.report.drift_check_method = self.params.drift_detection.method
            else:
                del self.report["drift_check_method"]

            self.report.check_results.critical_checks = self.critical_checks.to_dict()
            self.report.check_results.non_critical_checks = self.non_critical_checks.to_dict()

            return self.report.to_dict()
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

            report_dict = self._generate_report()
            save_to_yaml(report_dict, self.config.validation_report_filepath, label="Validation Report")

            is_valid = all(self.critical_checks.values())
            validated_filepath = self.config.validated_filepath if is_valid else None

            if is_valid:
                save_to_csv(self.df, validated_filepath, self.config.validated_dvc_path, label="Validated Data")
            else:
                logger.warning("Validation failed. Validated data not saved.")

            return DataValidationArtifact(
                validated_filepath=validated_filepath,
                validation_status=is_valid
            )

        except Exception as e:
            raise NetworkSecurityError(e, logger) from e
