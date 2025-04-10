from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType, FloatType, TimestampType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("SparkToPostgresql") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.jars", "/opt/spark/jars/postgresql-42.5.1.jar") \
    .getOrCreate()

# Read the data from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "TestTopic") \
    .load()

# Extract the value field from Kafka message (bytes -> string)
df = df.selectExpr("CAST(value AS STRING)")

# Convert JSON string to DataFrame
df = df.selectExpr("json_tuple(value, 'symbol', 'price', 'timestamp') as (symbol, price, timestamp)")

# Convert the price to float and timestamp to timestamp format
df = df.withColumn("price", col("price").cast(FloatType())) \
       .withColumn("timestamp", col("timestamp").cast(TimestampType()))

# Write the data to PostgreSQL using JDBC
def write_to_postgresql(batch_df, batch_id):
    batch_df.write \
        .jdbc(url="jdbc:postgresql://localhost:5432/stock_database", 
              table="stock_prices", 
              mode="append", 
              properties={"user": "postgres", "password": "postgres", "driver": "org.postgresql.Driver"})

# Write the stream to PostgreSQL
query = df.writeStream \
    .foreachBatch(write_to_postgresql) \
    .outputMode("append") \
    .start()

query.awaitTermination()
