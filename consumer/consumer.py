# consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructType, StructField, StringType,
    DoubleType, LongType, TimestampType
)
import os

# 1. Spark session with Kafka + Postgres support
spark = SparkSession.builder \
    .appName("StockPulseSparkConsumer") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
        "org.postgresql:postgresql:42.7.4"
    ) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Define schema of your Kafka JSON messages
schema = StructType([
    StructField("stream_ts", StringType()),
    StructField("index", StringType()),
    StructField("date", StringType()),
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("adj_close", DoubleType()),
    StructField("volume", LongType()),
    StructField("close_usd", DoubleType())
])

# 3. Read from Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "stock_ticks") \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Parse JSON values
parsed_df = raw_df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# 5. Cast types and add derived column
final_df = parsed_df \
    .withColumn("stream_ts", col("stream_ts").cast(TimestampType())) \
    .withColumn("date", col("date").cast("date")) \
    .withColumn("trade_value", col("close") * col("volume"))

# 6a. Write to Parquet (partitioned by index/date)
parquet_query = final_df.writeStream \
    .format("parquet") \
    .option("path", "file:///home/arjun/stock_pulse/lake/parquet") \
    .option("checkpointLocation", "file:///home/arjun/stock_pulse/chk/parquet") \
    .partitionBy("index", "date") \
    .outputMode("append") \
    .start()

user = os.getenv("PGUSER")
password = os.getenv("PGPASSWORD")

# 6b. Write to Postgres (via foreachBatch)
def write_to_postgres(batch_df, batch_id):
    (batch_df.write
        .format("jdbc")
        .option("url", "jdbc:postgresql://localhost:5432/stocks")
        .option("dbtable", "ticks_raw")
        .option("user", user)
        .option("password", password)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save())

pg_query = final_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .option("checkpointLocation", "file:///home/arjun/stock_pulse/chk/postgres") \
    .start()

# 7. Await termination
spark.streams.awaitAnyTermination()