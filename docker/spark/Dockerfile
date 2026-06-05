FROM apache/spark:3.5.1

USER root

RUN curl -sL https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
      -o /opt/spark/jars/hadoop-aws-3.3.4.jar && \
    curl -sL https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar \
      -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar && \
    echo "hadoop-aws-3.3.4.jar and aws-java-sdk-bundle-1.12.262.jar installed"

RUN pip install --no-cache-dir \
      boto3>=1.34 \
      pyyaml>=6.0 \
      structlog>=24.1 \
      python-dotenv>=1.0 \
      pandas \
      pyarrow \
      psycopg2-binary \
      sqlalchemy \
      s3fs \
      'dbt-core<1.9' \
      'dbt-postgres<1.9' \
      pyspark==3.5.3 \
      pytest \
      pytest-mock && \
    echo "Python dependencies installed"

USER spark
