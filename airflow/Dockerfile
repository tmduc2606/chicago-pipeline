FROM apache/airflow:2.10.5-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl procps && \
    rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# dbt-postgres (M4 warehouse) + pandas/pyarrow for Gold loader
RUN pip install --no-cache-dir dbt-postgres==1.8.2 pandas pyarrow s3fs
