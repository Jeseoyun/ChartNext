from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
from dotenv import load_dotenv

load_dotenv()

def create_spark_session():
    return SparkSession.builder \
        .appName("NewsStreamingJob") \
        .master(os.getenv("SPARK_MASTER_URL")) \
        .getOrCreate()

def process_stream(df, epoch_id):
    # 스트리밍 데이터 처리 로직
    df.write \
        .format("json") \
        .mode("append") \
        .save(os.getenv("HDFS_STREAM_PATH"))

def main():
    spark = create_spark_session()
    
    # 스키마 정의
    schema = StructType([
        StructField("category", StringType(), True),
        StructField("title", StringType(), True),
        StructField("url", StringType(), True),
        StructField("authors", ArrayType(
            StructType([
                StructField("name", StringType(), True),
                StructField("email", StringType(), True)
            ])
        ), True),
        StructField("time", StringType(), True),
        StructField("images", ArrayType(
            StructType([
                StructField("refid", StringType(), True),
                StructField("src", StringType(), True),
                StructField("caption", StringType(), True)
            ])
        ), True),
        StructField("content", ArrayType(
            StructType([
                StructField("refid", StringType(), True),
                StructField("text", StringType(), True)
            ])
        ), True)
    ])

    # 스트리밍 데이터 읽기
    streaming_df = spark.readStream \
        .format("json") \
        .schema(schema) \
        .load(os.getenv("HDFS_RAW_PATH"))

    # 스트리밍 처리
    query = streaming_df.writeStream \
        .foreachBatch(process_stream) \
        .trigger(processingTime=f"{os.getenv('STREAMING_INTERVAL')} seconds") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main() 