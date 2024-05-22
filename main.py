from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StringType, DoubleType

spark = SparkSession.builder.appName("BillionRowChallenge").getOrCreate()

# Reading from Kafka
kafka_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "your_topic") \
    .load()

# Assuming the value column contains the data as a JSON string
schema = StructType() \
    .add("field1", StringType()) \
    .add("field2", DoubleType())
    # Add more fields as per your data structure

json_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Perform transformations
transformed_df = json_df.withColumn("processed_time", current_timestamp())

# Writing to Parquet files
query = transformed_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "hdfs://path/to/output") \
    .option("checkpointLocation", "hdfs://path/to/checkpoint") \
    .start()

query.awaitTermination()
