"""Check which districts are not in the allowed set."""
from __future__ import annotations
import sys
from pathlib import Path
_src = Path("/opt/pipeline/src")
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from chicago_pipeline.common.spark_session import get_spark
from pyspark.sql import functions as F

spark = get_spark(app_name="CheckDistricts")
spark.sparkContext.setLogLevel("WARN")
df = spark.read.parquet("s3a://lake/silver/chicago_crime")

allowed = {1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,20,22,24,25}
actual = set(r.district for r in df.select("district").distinct().collect())
bad_values = actual - allowed
print(f"Allowed: {sorted(allowed)}")
print(f"Actual:  {sorted(actual)}")
print(f"Not in allowed: {sorted(bad_values)}")
print(f"Count of bad values: {df.filter(~F.col('district').isin(list(allowed))).count()}")
spark.stop()
