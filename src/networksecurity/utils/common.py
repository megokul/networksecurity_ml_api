import json
from pathlib import Path
from typing import Union
from urllib.parse import quote_plus

import pandas as pd
import yaml
from box import ConfigBox
from box.exceptions import BoxKeyError, BoxTypeError, BoxValueError
from ensure import ensure_annotations
from datetime import datetime, timezone

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """Read and parse a YAML file into a ConfigBox object."""
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
def create_directories(*paths: Path):
    """Create one or more directories (including parent folders if needed)."""
    try:
        for path in paths:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory at: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e


@ensure_annotations
def csv_to_json_convertor(source_filepath: Path, destination_filepath: Path):
    """
    Convert a CSV file to a list of JSON records and optionally save it.
    """
    try:
        df = pd.read_csv(source_filepath).reset_index(drop=True)
        records = df.to_dict(orient="records")

        # Ensure output directory exists
        parent_dir = destination_filepath.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory for JSON output at: '{parent_dir.as_posix()}'")

        with destination_filepath.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)

        logger.info(f"CSV converted and saved to: '{destination_filepath.as_posix()}'")
        return records

    except Exception as e:
        raise NetworkSecurityError(e, logger) from e


@ensure_annotations
def replace_username_password_in_uri(base_uri: str, username: str, password: str) -> str:
    """
    Safely replace <username> and <password> in a MongoDB URI with encoded credentials.
    """
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
    """
    Save a dictionary to one or more YAML file paths.

    Args:
        data (dict): The dictionary to be written as YAML.
        *paths (Path): One or more output file paths.
        label (str): Descriptive label used in logs.
    """
    try:
        for path in paths:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as file:
                yaml.dump(data, file, sort_keys=False)
            logger.info(f"{label} saved to: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e

@ensure_annotations
def save_to_csv(df: pd.DataFrame, *paths: Path, label: str):
    """
    Save a DataFrame to one or more CSV file paths.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        *paths (Path): One or more output file paths.
        label (str): Descriptive label used in logs.
    """
    try:
        for path in paths:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
            logger.info(f"{label} saved to: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e
    

@ensure_annotations
def save_to_json(data: dict | list, *paths: Path, label: str):
    """
    Save a dictionary or list to one or more JSON file paths.

    Args:
        data (dict | list): The data to be written as JSON.
        *paths (Path): One or more output file paths.
        label (str): Descriptive label used in logs.
    """
    try:
        for path in paths:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info(f"{label} saved to: '{path.as_posix()}'")
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e