import os
import tempfile

import kaggle
import pandas as pd

pd.DataFrame.iteritems = pd.DataFrame.items

import pyspark
from pyspark.ml import Pipeline
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.linalg import DenseVector
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import expr, udf
from pyspark.sql.types import ArrayType, DoubleType, StringType, StructField, StructType
from transformers import pipeline

from dagster import Output, asset


# UDF to convert SparseVector to a dense array
def sparse_to_dense_array(vector):
    return vector.toArray()


@asset(
    name="nlp_mental_health_conversations_raw",
    description=(
        "Fetches mental health conversations from Kaggle, loads them "
        "into a Spark DataFrame with columns [Context, Response], and "
        "writes it to an Iceberg table on Minio."
    ),
)
def nlp_mental_health_conversations_raw():
    """
    Dagster asset to ingest raw mental health conversation data from Kaggle,
    transform it to a two-column schema (Context, Response), and store it
    in an Apache Iceberg table in Minio.
    """
    dataset_name = "thedevastator/nlp-mental-health-conversations"
    df_pandas = get_csv_from_kaggle(dataset_name)

    spark = get_spark_session()
    schema = StructType(
        [
            StructField("Context", StringType(), True),
            StructField("Response", StringType(), True),
        ]
    )
    spark_df = spark.createDataFrame(
        df_pandas[["Context", "Response"]].dropna(how="any"), schema=schema
    )
    table_full_name = "nessie.mental_health_conversations_raw"
    spark_df.writeTo(table_full_name).createOrReplace()
    num_records = spark_df.count()
    spark.stop()

    return Output({"rows_written": num_records})


def get_csv_from_kaggle(dataset_name) -> pd.DataFrame:
    with tempfile.TemporaryDirectory() as temp_dir:
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(dataset_name, path=temp_dir, unzip=True)
        csv_file_path = os.path.join(temp_dir, "train.csv")
        return pd.read_csv(csv_file_path)


def get_spark_session():
    NESSIE_URI = os.environ.get("NESSIE_URI")  ## Nessie Server URI
    WAREHOUSE = os.environ.get("WAREHOUSE")  ## BUCKET TO WRITE DATA TOO
    AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")  ## AWS CREDENTIALS
    AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")  ## AWS CREDENTIALS
    AWS_S3_ENDPOINT = os.environ.get("AWS_S3_ENDPOINT")  ## MINIO ENDPOINT
    conf = (
        pyspark.SparkConf()
        .setAppName("app_name")
        .set(
            "spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.1,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.3_2.12:0.67.0,software.amazon.awssdk:bundle:2.17.178,software.amazon.awssdk:url-connection-client:2.17.178",
        )
        .set(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions",
        )
        .set("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
        .set("spark.sql.catalog.nessie.uri", NESSIE_URI)
        .set("spark.sql.catalog.nessie.ref", "main")
        .set("spark.sql.catalog.nessie.authentication.type", "NONE")
        .set(
            "spark.sql.catalog.nessie.catalog-impl",
            "org.apache.iceberg.nessie.NessieCatalog",
        )
        .set("spark.sql.catalog.nessie.s3.endpoint", AWS_S3_ENDPOINT)
        .set("spark.sql.catalog.nessie.warehouse", WAREHOUSE)
        .set("spark.sql.catalog.nessie.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
        .set("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY)
        .set("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_KEY)
    )
    spark = SparkSession.builder.config(conf=conf).getOrCreate()
    return spark


@asset(
    name="nlp_mental_health_conversations_stg",
    deps=["nlp_mental_health_conversations_raw"],
    description=(
        "Cleans the raw mental health conversations data, and writes it to an Iceberg table on Minio."
    ),
)
def nlp_mental_health_conversations_stg():
    spark = get_spark_session()
    raw_table = "nessie.mental_health_conversations_raw"
    raw_df = spark.table(raw_table)
    raw_df = raw_df.withColumnRenamed("Context", "context")
    raw_df = raw_df.withColumnRenamed("Response", "response")

    staging_table = "nessie.mental_health_conversations_stg"
    raw_df.writeTo(staging_table).createOrReplace()

    return Output({"rows_written": raw_df.count()})


@asset(
    name="nlp_mental_health_model_training_gold",
    deps=["nlp_mental_health_conversations_stg"],
    description=("Feature engineering and model training data set."),
)
def nlp_mental_health_model_training_gold():
    """Performs feature engineering and creates training dataset"""
    spark = SparkConfig.get_session()
    raw_df = spark.table("nessie.mental_health_conversations_stg").limit(100)

    # Apply sentiment analysis
    analyzer = SentimentAnalyzer(spark)
    df_with_sentiment = raw_df.transform(
        lambda df: analyzer.analyze_text(df, "context")
    ).transform(lambda df: analyzer.analyze_text(df, "response"))

    # Transform sentiment labels to one-hot encoding
    df_transformed = _create_sentiment_features(df_with_sentiment)

    # Write to gold table
    df_transformed.writeTo(
        "nessie.nlp_mental_health_model_training_gold"
    ).createOrReplace()
    return Output({"rows_written": df_transformed.count()})


def _create_sentiment_features(df):
    """Creates one-hot encoded features from sentiment labels"""
    sentiment_categories = ["positive", "negative", "neutral"]

    for col_prefix in ["context", "response"]:
        for category in sentiment_categories:
            df = df.withColumn(
                f"{col_prefix}_sentiment_{category}",
                F.when(F.col(f"{col_prefix}_sentiment_label") == category, 1).otherwise(
                    0
                ),
            )

    return df.drop("context_sentiment_label", "response_sentiment_label")


class SparkConfig:
    """Handles Spark configuration and session management"""

    @staticmethod
    def get_session():
        conf = SparkConfig._build_config()
        return SparkSession.builder.config(conf=conf).getOrCreate()

    @staticmethod
    def _build_config():
        env = {
            "NESSIE_URI": os.environ.get("NESSIE_URI"),
            "WAREHOUSE": os.environ.get("WAREHOUSE"),
            "AWS_ACCESS_KEY": os.environ.get("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
            "AWS_S3_ENDPOINT": os.environ.get("AWS_S3_ENDPOINT"),
        }

        return (
            pyspark.SparkConf()
            .setAppName("mental_health_analytics")
            .set(
                "spark.jars.packages",
                "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.1,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.3_2.12:0.67.0,software.amazon.awssdk:bundle:2.17.178,software.amazon.awssdk:url-connection-client:2.17.178",
            )
            .set(
                "spark.sql.extensions",
                "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions",
            )
            .set("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
            .set("spark.sql.catalog.nessie.uri", env["NESSIE_URI"])
            .set("spark.sql.catalog.nessie.ref", "main")
            .set("spark.sql.catalog.nessie.authentication.type", "NONE")
            .set(
                "spark.sql.catalog.nessie.catalog-impl",
                "org.apache.iceberg.nessie.NessieCatalog",
            )
            .set("spark.sql.catalog.nessie.s3.endpoint", env["AWS_S3_ENDPOINT"])
            .set("spark.sql.catalog.nessie.warehouse", env["WAREHOUSE"])
            .set(
                "spark.sql.catalog.nessie.io-impl", "org.apache.iceberg.aws.s3.S3FileIO"
            )
            .set("spark.hadoop.fs.s3a.access.key", env["AWS_ACCESS_KEY"])
            .set("spark.hadoop.fs.s3a.secret.key", env["AWS_SECRET_KEY"])
        )


class KaggleDataLoader:
    """Handles data loading from Kaggle"""

    @staticmethod
    def load_csv(dataset_name) -> pd.DataFrame:
        with tempfile.TemporaryDirectory() as temp_dir:
            kaggle.api.authenticate()
            kaggle.api.dataset_download_files(dataset_name, path=temp_dir, unzip=True)
            csv_file_path = os.path.join(temp_dir, "train.csv")
            return pd.read_csv(csv_file_path)


class SentimentAnalyzer:
    """Handles sentiment analysis operations"""

    def __init__(self, spark_session):
        self.spark = spark_session
        self._init_sentiment_pipeline()

    def _init_sentiment_pipeline(self):
        pipeline_config = {
            "model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "tokenizer": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "truncation": True,
            "padding": True,
            "max_length": 512,
        }
        sentiment_pipeline = pipeline("sentiment-analysis", **pipeline_config)
        self.pipeline = self.spark.sparkContext.broadcast(sentiment_pipeline)

    def analyze_text(self, df, text_column):
        """Adds sentiment analysis columns to the dataframe"""
        sentiment_label_udf = udf(self._get_sentiment_label, StringType())
        sentiment_score_udf = udf(self._get_sentiment_score, DoubleType())

        prefix = f"{text_column}_sentiment"
        return df.withColumn(
            f"{prefix}_label", sentiment_label_udf(df[text_column])
        ).withColumn(f"{prefix}_score", sentiment_score_udf(df[text_column]))

    def _get_sentiment_label(self, text):
        return self.pipeline.value(text)[0]["label"]

    def _get_sentiment_score(self, text):
        return self.pipeline.value(text)[0]["score"]
