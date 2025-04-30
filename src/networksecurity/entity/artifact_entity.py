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
    x_preprocessor_filepath: Path
    y_preprocessor_filepath: Path

    def __repr__(self) -> str:
        x_train_str = self.x_train_filepath.as_posix() if self.x_train_filepath else "None"
        y_train_str = self.y_train_filepath.as_posix() if self.y_train_filepath else "None"
        x_val_str = self.x_val_filepath.as_posix() if self.x_val_filepath else "None"
        y_val_str = self.y_val_filepath.as_posix() if self.y_val_filepath else "None"
        x_test_str = self.x_test_filepath.as_posix() if self.x_test_filepath else "None"
        y_test_str = self.y_test_filepath.as_posix() if self.y_test_filepath else "None"
        x_preprocessor_str = self.x_preprocessor_filepath.as_posix() if self.x_preprocessor_filepath else "None"
        y_preprocessor_str = self.y_preprocessor_filepath.as_posix() if self.y_preprocessor_filepath else "None"

        return (
            "\nData Transformation Artifact:\n"
            f"  - X-Train Data Path:    '{x_train_str}'\n"
            f"  - Y-Train Data Path:    '{y_train_str}'\n"
            f"  - X-Val Data Path:      '{x_val_str}'\n"
            f"  - Y-Val Data Path:      '{y_val_str}'\n"
            f"  - X-Test Data Path:     '{x_test_str}'\n"
            f"  - Y-Test Data Path:     '{y_test_str}'\n"
            f"  - X-Processor Path:     '{x_preprocessor_str}'\n"
            f"  - Y-Processor Path:     '{y_preprocessor_str}'\n"
        )


@dataclass(frozen=True)
class ModelTrainerArtifact:
    trained_model_filepath: Path
    training_report_filepath: Path
    x_train_filepath: Path
    y_train_filepath: Path
    x_val_filepath: Path
    y_val_filepath: Path
    x_test_filepath: Path
    y_test_filepath: Path

    def __repr__(self) -> str:
        return (
            "\nModel Trainer Artifact:\n"
            f"  - Trained Model Path:   '{self.trained_model_filepath.as_posix()}'\n"
            f"  - Training Report Path: '{self.training_report_filepath.as_posix()}'\n"
            f"  - X Train Path: '{self.x_train_filepath.as_posix()}'\n"
            f"  - Y Train Path: '{self.y_train_filepath.as_posix()}'\n"
            f"  - X Val Path:   '{self.x_val_filepath.as_posix()}'\n"
            f"  - Y Val Path:   '{self.y_val_filepath.as_posix()}'\n"
            f"  - X Test Path:  '{self.x_test_filepath.as_posix()}'\n"
            f"  - Y Test Path:  '{self.y_test_filepath.as_posix()}'"
        )


@dataclass(frozen=True)
class ModelEvaluationArtifact:
    evaluation_report_filepath: Path

    def __repr__(self) -> str:
        report_str = self.evaluation_report_filepath.as_posix() if self.evaluation_report_filepath else "None"

        return (
            "\nModel Evaluation Artifact:\n"
            f"  - Evaluation Report Path: '{report_str}'\n"
        )

@dataclass(frozen=True)
class ModelPusherArtifact:
    pushed_model_local_path: Path
    pushed_model_s3_path: str

    def __repr__(self) -> str:
        local_str = self.pushed_model_local_path.as_posix() if self.pushed_model_local_path else "None"
        s3_str = self.pushed_model_s3_path if self.pushed_model_s3_path else "None"
        return (
            "\nModel Pusher Artifact:\n"
            f"  - Local Path: '{local_str}'\n"
            f"  - S3 Path:    '{s3_str}'\n"
        )


@dataclass(frozen=True)
class ModelPusherArtifact:
    pushed_model_local_path: Path
    pushed_model_s3_path: str | None = None  # Optional if S3 upload is disabled

    def __repr__(self) -> str:
        return (
            "\nModel Pusher Artifact:\n"
            f"  - Local Model Path: {self.pushed_model_local_path.as_posix()}\n"
            f"  - S3 Model Path:    {self.pushed_model_s3_path or 'Not uploaded'}\n"
        )