from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, FloatType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

# Define the schema of the incoming JSON data
schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("price", FloatType(), True),
    StructField("timestamp", StringType(), True)
])

# Read data from Kafka topic
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "TestTopic") \
    .load()

# Convert the Kafka message value (which is in JSON format) to a structured DataFrame
df = df.selectExpr("CAST(value AS STRING) as json") \
       .select(from_json(col("json"), schema).alias("data")) \
       .select("data.*")

# Print the streaming data to the console
query = df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Keep the streaming process running
query.awaitTermination()
