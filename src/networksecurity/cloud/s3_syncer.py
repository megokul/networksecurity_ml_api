from pathlib import Path
import os
import boto3
from botocore.exceptions import ClientError

from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError


class S3Syncer:
    """
    Handles syncing of files and directories to AWS S3 with logging and error handling.
    """

    def __init__(self, bucket_name: str, region: str = "us-east-1") -> None:
        try:
            self.bucket_name = bucket_name
            self.s3_client = boto3.client("s3", region_name=region)
            logger.info(f"S3Syncer initialized for bucket '{bucket_name}' in region '{region}'")
        except Exception as e:
            logger.exception("S3 client initialization failed")
            raise NetworkSecurityError(e, logger) from e

    def upload_file(self, local_path: Path, s3_key: str) -> None:
        """
        Upload a single file to S3.
        """
        try:
            local_path = Path(local_path)
            if not local_path.is_file():
                raise FileNotFoundError(f"Local file not found: {local_path.as_posix()}")

            self.s3_client.upload_file(
                Filename=str(local_path),
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"File uploaded to S3: {local_path} → s3://{self.bucket_name}/{s3_key}")

        except ClientError as e:
            logger.error(f"AWS ClientError while uploading to S3: {e}")
            raise NetworkSecurityError(e, logger) from e
        except Exception as e:
            logger.error(f"Unexpected error while uploading file to S3: {e}")
            raise NetworkSecurityError(e, logger) from e

    def sync_directory(self, local_dir: Path, s3_prefix: str = "") -> None:
        """
        Recursively upload a local directory to the specified S3 prefix.
        """
        try:
            local_dir = Path(local_dir)
            if not local_dir.is_dir():
                raise NotADirectoryError(f"Local directory not found: {local_dir.as_posix()}")

            for root, _, files in os.walk(local_dir):
                for file in files:
                    local_file_path = Path(root) / file
                    relative_path = local_file_path.relative_to(local_dir)
                    s3_key = (Path(s3_prefix) / relative_path).as_posix()

                    self.upload_file(local_file_path, s3_key)

            logger.info(f"Directory synced to S3: {local_dir} → s3://{self.bucket_name}/{s3_prefix}")

        except Exception as e:
            logger.error("Failed to sync directory to S3")
            raise NetworkSecurityError(e, logger) from e
