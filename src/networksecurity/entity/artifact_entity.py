from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionArtifact:
    raw_artifact_path: Path
    cleaned_artifact_path: Path
    raw_dvc_path: Path
    cleaned_dvc_path: Path
