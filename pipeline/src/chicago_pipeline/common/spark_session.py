from pyspark.sql import SparkSession

from .settings import settings


def get_spark(app_name: str = "ChicagoPipeline") -> SparkSession:
    cfg = settings.storage
    builder = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.endpoint", cfg.get("endpoint", "http://minio:9000"))
        .config("spark.hadoop.fs.s3a.access.key", cfg.get("access_key", "minio"))
        .config("spark.hadoop.fs.s3a.secret.key", cfg.get("secret_key", "minio123"))
        .config(
            "spark.hadoop.fs.s3a.path.style.access",
            str(cfg.get("path_style_access", True)).lower(),
        )
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    )
    return builder.getOrCreate()
