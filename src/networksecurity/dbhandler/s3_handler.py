from pathlib import Path
import os
import boto3
from botocore.exceptions import ClientError

import pandas as pd

from src.networksecurity.entity.config_entity import S3HandlerConfig
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.logging import logger
from src.networksecurity.dbhandler.base_handler import DBHandler


class S3Handler(DBHandler):
    """
    AWS S3 Handler implementing DBHandler interface.
    Supports file upload and directory sync.
    """

    def __init__(self, config: S3HandlerConfig):
        try:
            self.config = config
            self._client = boto3.client("s3", region_name=self.config.aws_region)
            logger.info(f"S3Handler initialized for bucket '{self.config.bucket_name}' in region '{self.config.aws_region}'")
        except Exception as e:
            logger.exception("Failed to initialize S3 client")
            raise NetworkSecurityError(e, logger) from e

    def close(self) -> None:
        """
        No persistent connection in S3 client.
        Included for interface compatibility.
        """
        logger.info("S3Handler close() called. No persistent connection to close.")

    def load_from_source(self) -> pd.DataFrame:
        """
        Not supported: Loading data as DataFrame from S3 is not implemented.
        """
        raise NotImplementedError("S3Handler does not support DataFrame loading from S3.")

    def upload_file(self, local_path: Path, s3_key: str) -> None:
        """
        Upload a single file to S3.

        Args:
            local_path (Path): Local file path.
            s3_key (str): Destination S3 key (folder/filename).
        """
        try:
            local_path = Path(local_path)
            if not local_path.is_file():
                raise FileNotFoundError(f"Local file not found: {local_path.as_posix()}")

            self._client.upload_file(
                Filename=str(local_path),
                Bucket=self.config.bucket_name,
                Key=s3_key
            )
            logger.info(f"Uploaded: {local_path.as_posix()} -> s3://{self.config.bucket_name}/{s3_key}")

        except ClientError as e:
            logger.error(f"AWS ClientError while uploading to S3: {e}")
            raise NetworkSecurityError(e, logger) from e
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            raise NetworkSecurityError(e, logger) from e

    def sync_directory(self, local_dir: Path, s3_prefix: str) -> None:
        """
        Uploads a directory to S3 recursively.

        Args:
            local_dir (Path): Local directory to sync.
            s3_prefix (str): S3 prefix (target folder path).
        """
        try:
            local_dir = Path(local_dir)
            if not local_dir.is_dir():
                raise NotADirectoryError(f"Local directory not found: {local_dir.as_posix()}")

            logger.info(f"Starting S3 sync: {local_dir.as_posix()} -> s3://{self.config.bucket_name}/{s3_prefix}")

            for root, _, files in os.walk(local_dir):
                for file in files:
                    local_file_path = Path(root) / file
                    relative_path = local_file_path.relative_to(local_dir)
                    remote_key = (Path(s3_prefix) / relative_path).as_posix()
                    self.upload_file(local_file_path, remote_key)

            logger.info(f"Directory synced to S3: {local_dir.as_posix()} -> s3://{self.config.bucket_name}/{s3_prefix}")

        except Exception as e:
            logger.error("Directory sync to S3 failed.")
            raise NetworkSecurityError(e, logger) from e
