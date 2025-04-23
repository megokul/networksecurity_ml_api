from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class DataIngestionArtifact:
    raw_artifact_path: Path
    ingested_data_filepath: Path
    raw_dvc_path: Path

    def __repr__(self) -> str:
        raw_artifact_str = self.raw_artifact_path.as_posix() if self.raw_artifact_path else "None"
        raw_dvc_str = self.raw_dvc_path.as_posix() if self.raw_dvc_path else "None"
        ingested_data_str = self.ingested_data_filepath.as_posix() if self.ingested_data_filepath else "None"

        return (
            "\nData Ingestion Artifact:\n"
            f"  - Raw Artifact:         '{raw_artifact_str}'\n"
            f"  - Raw DVC Path:         '{raw_dvc_str}'\n"
            f"  - Ingested Data Path:   '{ingested_data_str}'\n"
        )


@dataclass(frozen=True)
class DataValidationArtifact:
    validated_filepath: Path
    validation_status: bool

    def __repr__(self) -> str:
        validated_str = self.validated_filepath.as_posix() if self.validated_filepath else "None"

        return (
            "\nData Validation Artifact:\n"
            f"  - Validated Data Path: '{validated_str}'\n"
            f"  - Validation Status:   '{self.validation_status}'\n"
        )

@dataclass(frozen=True)
class DataTransformationArtifact:
    x_train_filepath: Path
    y_train_filepath: Path
    x_val_filepath: Path
    y_val_filepath: Path
    x_test_filepath: Path
    y_test_filepath: Path

    def __repr__(self) -> str:
        x_train_str = self.x_train_filepath.as_posix() if self.x_train_filepath else "None"
        y_train_str = self.y_train_filepath.as_posix() if self.y_train_filepath else "None"
        x_val_str = self.x_val_filepath.as_posix() if self.x_val_filepath else "None"
        y_val_str = self.y_val_filepath.as_posix() if self.y_val_filepath else "None"
        x_test_str = self.x_test_filepath.as_posix() if self.x_test_filepath else "None"
        y_test_str = self.y_test_filepath.as_posix() if self.y_test_filepath else "None"

        return (
            "\nData Transformation Artifact:\n"
            f"  - X-Train Data Path:    '{x_train_str}'\n"
            f"  - Y-Train Data Path:    '{y_train_str}'\n"
            f"  - X-Val Data Path:      '{x_val_str}'\n"
            f"  - Y-Val Data Path:      '{y_val_str}'\n"
            f"  - X-Test Data Path:     '{x_test_str}'\n"
            f"  - Y-Test Data Path:     '{y_test_str}'\n"
        )
