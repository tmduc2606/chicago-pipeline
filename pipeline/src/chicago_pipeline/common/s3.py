from __future__ import annotations

import boto3
from botocore.config import Config as B3Config

from .settings import settings


def s3_client() -> boto3.client:
    cfg = settings.storage
    return boto3.client(
        "s3",
        endpoint_url=cfg.get("endpoint", "http://minio:9000"),
        aws_access_key_id=cfg.get("access_key", "minio"),
        aws_secret_access_key=cfg.get("secret_key", "minio123"),
        config=B3Config(s3={"addressing_style": "path"}),
    )
