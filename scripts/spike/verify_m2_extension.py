"""One-off verification of M2 Extension output."""
from __future__ import annotations

import sys
from pathlib import Path

_src = Path("/opt/pipeline/src")
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from chicago_pipeline.common.spark_session import get_spark
from chicago_pipeline.common.settings import settings
from pyspark.sql import functions as F

spark = get_spark(app_name="VerifyM2Extension")
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("s3a://lake/silver/chicago_crime")
print(f"Row count: {df.count()}")
print(f"Column count: {len(df.columns)}")
print(f"Columns: {sorted(df.columns)}")

df.select(
    "id", "date", "is_arrested", "is_domestic", "is_domestic_arrest",
    "date_year", "date_month", "date_dow",
    "updated_on_ts", "hours_to_update"
).show(5, truncate=False)

print("--- is_arrested mean (cast to int) ---")
df.agg(F.mean(F.col("is_arrested").cast("int")).alias("is_arrested_mean")).show()

spark.stop()
print("VERIFICATION PASSED")
