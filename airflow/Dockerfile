FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl procps wget openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

ARG SPARK_VERSION=3.5.1
ARG HADOOP_VERSION=3
RUN wget -q "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -O /tmp/spark.tgz && \
    tar xzf /tmp/spark.tgz -C /opt && \
    ln -s "/opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" /opt/spark && \
    rm /tmp/spark.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH="$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin"

RUN pip install --no-cache-dir pyspark==3.5.1

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
