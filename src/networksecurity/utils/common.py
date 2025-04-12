"""Utility to read YAML configuration files and return them as ConfigBox objects.

Provides structured exception handling, logging, and PEP-compliant error chaining.
"""

import json
from pathlib import Path

import pandas as pd
import yaml
from box import ConfigBox
from box.exceptions import BoxKeyError, BoxTypeError, BoxValueError
from ensure import ensure_annotations

from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger


def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """Read and parse a YAML file into a ConfigBox object.

    Args:
        path_to_yaml (Path): Path to the YAML file.

    Returns:
        ConfigBox: Parsed content with dot-access enabled.

    Raises:
        NetworkSecurityError: If the file is missing, empty, or invalid.

    """
    if not path_to_yaml.exists():
        msg = f"YAML file not found: '{path_to_yaml}'"
        logger.error(msg)  # Log missing file
        raise NetworkSecurityError(FileNotFoundError(msg), logger)  # Raise custom exception

    try:
        with path_to_yaml.open("r") as f:
            content = yaml.safe_load(f)  # Load YAML safely into Python dictionary

    except (BoxValueError, BoxTypeError, BoxKeyError, yaml.YAMLError) as e:
        logger.error(f"Failed to load YAML from {path_to_yaml.as_posix()}: {e}")  # Log known parsing errors
        raise NetworkSecurityError(e, logger) from e  # Wrap and re-raise as custom error

    except Exception as e:
        logger.error(f"Unexpected error reading YAML file: {e}")  # Catch-all for unforeseen issues
        raise NetworkSecurityError(e, logger) from e

    if content is None:
        msg = "YAML file is empty or improperly formatted."
        logger.error(msg)  # Log empty content case
        raise NetworkSecurityError(ValueError(msg), logger)  # Raise custom exception

    logger.info(f"YAML loaded successfully from: '{path_to_yaml.as_posix()}'")  # Log success
    return ConfigBox(content)  # Return dot-accessible config object

@ensure_annotations
def create_directories(*path_to_directories: Path):
    """Create one or more directories, ensuring parent directories are created as needed.

    Args:
        *path_to_directories (Path): One or more directory paths to create.

    Raises:
        NetworkSecurityError: If any unexpected error occurs during directory creation.

    """
    try:
        for path in path_to_directories:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory at: '{path.as_posix()}'")  # ✅ Fix: POSIX-style path
    except Exception as e:
        raise NetworkSecurityError(e, logger) from e


@ensure_annotations
def csv_to_json_convertor(source_filepath: Path, destination_filepath: Path):
    """
    Convert a CSV file to a list of JSON records and save to destination.

    If the destination folder doesn't exist, it will be created and logged.

    Args:
        source_filepath (Path): Path to the input CSV file.
        destination_filepath (Path): Path to save the resulting JSON file.

    Returns:
        list[dict]: List of JSON-compatible records.
    """
    try:
        # Read and process the CSV data
        data = pd.read_csv(source_filepath)
        data = data.reset_index(drop=True)
        records = data.to_dict(orient="records")

        # Ensure the parent directory exists
        parent_dir = destination_filepath.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory for JSON output at: '{parent_dir}'")

        # Save the JSON file
        with destination_filepath.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)

        logger.info(f"CSV converted and saved to: '{destination_filepath}'")
        return records

    except Exception as e:
        raise NetworkSecurityError(e, logger) from e

from urllib.parse import quote_plus

@ensure_annotations
def replace_username_password_in_uri(
    base_uri: str,
    username: str,
    password: str,
) -> str:
    """
    Replace <username> and <password> in a MongoDB URI with provided credentials.

    Args:
        base_uri (str): MongoDB URI template containing <username> and <password>.
        username (str): MongoDB username.
        password (str): MongoDB password.

    Returns:
        str: Formatted MongoDB URI with encoded credentials.

    Raises:
        ValueError: If base_uri, username, or password are missing.
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
