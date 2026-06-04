#!/usr/bin/env bash
# Gold Query Tool — batch test (runs INSIDE container)
set -e

SCRIPT="/opt/pipeline/scripts/explore/gold_query.py"
SPARK="/opt/spark/bin/spark-submit"
MASTER="spark://spark-master:7077"

echo "Running 38 commands through gold_query.py ..."
echo ""
cat <<'EOF' | $SPARK --master $MASTER \
  --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
  --conf spark.hadoop.fs.s3a.access.key=minio \
  --conf spark.hadoop.fs.s3a.secret.key=change_me_local \
  --conf spark.hadoop.fs.s3a.path.style.access=true \
  --conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
  $SCRIPT 2>&1 | grep -v "^26/" | grep -v "^$"
help
tables
schema fact
schema time
schema offense
schema location
schema case
head fact 3
head time 3
head offense 3
head location 3
head case 3
count fact
count fact year
count fact arrest
count fact domestic
count offense primary_type
count offense fbi_code
count location district
count location is_downtown
filter fact arrest True
filter fact arrest False
filter fact domestic True
filter fact year 2024
agg fact hours_to_update mean
agg fact hours_to_update max
agg fact hours_to_update min
agg offense offense_id count
agg location distance_to_downtown_km mean
join
search offense primary_type THEFT
search offense primary_type BATTERY
search offense primary_type ASSAULT
search location block W 79TH
search case case_number HX
qotd
qotd
quit
EOF
