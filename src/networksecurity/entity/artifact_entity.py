from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataIngestionArtifact:
    raw_artifact_path: Path
    ingested_data_filepath: Path
    raw_dvc_path: Path

    def __repr__(self) -> str:
        return (
            "\nData Ingestion Artifact Paths:\n"
            f"  - Raw Artifact:     {self.raw_artifact_path}\n"
            f"  - Raw DVC Path:     {self.raw_dvc_path}\n"
            f"  - Ingested Data Path:     {self.ingested_data_filepath}\n"
        )


@dataclass(frozen=True)
class DataValidationArtifact:
    validated_path: Path | None
    drift_report_path: Path
    validation_status: bool

    def __repr__(self) -> str:
        return (
            "\nData Validation Artifact Paths:\n"
            f"  - Validated Data Path: {self.validated_path}\n"
            f"  - Drift Report Path:   {self.drift_report_path}\n"
            f"  - Validation Status:   {self.validation_status}"
        )
