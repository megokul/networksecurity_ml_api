import json
import joblib
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from box import ConfigBox
from box.exceptions import BoxKeyError, BoxTypeError, BoxValueError
from urllib.parse import quote_plus
from ensure import ensure_annotations

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    if not path_to_yaml.exists():
        msg = f"YAML file not found: '{path_to_yaml}'"
        logger.error(msg)
        raise NetworkSecurityError(FileNotFoundError(msg), logger)

    try:
        with path_to_yaml.open("r") as f:
            content = yaml.safe_load(f)
    except (BoxValueError, BoxTypeError, BoxKeyError, yaml.YAMLError) as e:
        logger.error(f"Failed to load YAML from {path_to_yaml.as_posix()}: {e}")
        raise NetworkSecurityError(e, logger) from e
    except Exception as e:
        logger.error(f"Unexpected error reading YAML file: {e}")
        raise NetworkSecurityError(e, logger) from e

    if content is None:
        msg = "YAML file is empty or improperly formatted."
        logger.error(msg)
        raise NetworkSecurityError(ValueError(msg), logger)

    logger.info(f"YAML loaded successfully from: '{path_to_yaml.as_posix()}'")
    return ConfigBox(content)


@ensure_annotations
def csv_to_json_convertor(source_filepath: Path, destination_filepath: Path):
    """
    Convert a CSV file to a list of JSON records and optionally save it.
    """
    try:
        if not source_filepath.exists():
            raise FileNotFoundError(f"CSV source file not found: '{source_filepath.as_posix()}'")

        df = pd.read_csv(source_filepath).reset_index(drop=True)
        records = df.to_dict(orient="records")

        parent_dir = destination_filepath.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory for JSON output: '{parent_dir.as_posix()}'")
        else:
            logger.info(f"Directory already exists for JSON output: '{parent_dir.as_posix()}'")

        with destination_filepath.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)

        logger.info(f"CSV converted and saved to: '{destination_filepath.as_posix()}'")
        return records

    except Exception as e:
        raise NetworkSecurityError(e, logger) from e

    except Exception as e:
        raise NetworkSecurityError(e, logger) from e


@ensure_annotations
def replace_username_password_in_uri(base_uri: str, username: str, password: str) -> str:
    if not all([base_uri, username, password]):
        raise ValueError("base_uri, username, and password must all be provided.")

    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)

    return (
        base_uri
        .replace("<username>", encoded_username)
        .replace("<password>", encoded_password)
    )


@ensure_annotations
def save_to_yaml(data: dict, *paths: Path, label: str):
    try:
        for path in paths:
            path = Path(path)
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory for {label}: '{path.parent.as_posix()}'")
            else:
                logger.info(f"Directory already exists for {label}: '{path.parent.as_posix()}'")

            with open(path, "w") as file:
                yaml.dump(data, file, sort_keys=False)

            logger.info(f"{label} saved to: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e


@ensure_annotations
def save_to_csv(df: pd.DataFrame, *paths: Path, label: str):
    try:
        for path in paths:
            path = Path(path)
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory for {label}: '{path.parent.as_posix()}'")
            else:
                logger.info(f"Directory already exists for {label}: '{path.parent.as_posix()}'")

            df.to_csv(path, index=False)
            logger.info(f"{label} saved to: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e

@ensure_annotations
def save_array(array: np.ndarray | pd.Series, *paths: Path, label: str):
    """
    Saves a NumPy array or pandas Series to the specified paths in `.npy` format.

    Args:
        array (Union[np.ndarray, pd.Series]): Data to save.
        *paths (Path): One or more file paths.
        label (str): Label for logging.
    """
    try:
        # Convert Series to ndarray if needed
        array = np.asarray(array)

        for path in paths:
            path = Path(path)

            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory for {label}: '{path.parent.as_posix()}'")
            else:
                logger.info(f"Directory already exists for {label}: '{path.parent.as_posix()}'")

            # # Ensure file ends with `.npy`
            # if path.suffix != ".npy":
            #     path = path.with_suffix(".npy")

            np.save(path, array)
            logger.info(f"{label} saved to: '{path.as_posix()}'")

    except Exception as e:
        raise NetworkSecurityError(e, logger) from e

@ensure_annotations
def save_to_json(data: dict, *paths: Path, label: str):
    try:
        for path in paths:
            path = Path(path)
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory for {label}: '{path.parent.as_posix()}'")
            else:
                logger.info(f"Directory already exists for {label}: '{path.parent.as_posix()}'")

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            logger.info(f"{label} saved to: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e


@ensure_annotations
def read_csv(path: Path, label: str) -> pd.DataFrame:
    try:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{label} not found at path: {path.as_posix()}")

        df = pd.read_csv(path)
        logger.info(f"{label} loaded from: '{path.as_posix()}'")
        return df

    except Exception as e:
        raise NetworkSecurityError(e, logger) from e


@ensure_annotations
def save_object(obj: object, path: Path, label: str):
    try:
        path = Path(path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory for {label}: '{path.parent.as_posix()}'")
        else:
            logger.info(f"Directory already exists for {label}: '{path.parent.as_posix()}'")

        joblib.dump(obj, path)
        logger.info(f"{label} saved to: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e
