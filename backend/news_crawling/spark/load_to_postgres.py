from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, monotonically_increasing_id, to_json, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, IntegerType
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
db_url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("NewsToPostgres") \
    .config("spark.jars", "/usr/local/spark/jars/postgresql-42.7.3.jar") \
    .getOrCreate()

# JSON 파일 읽기
hdfs_data_path = f"hdfs://{os.getenv('HDFS_URL')}{os.getenv('HDFS_DATA_PATH')}"
df = spark.read.option("multiline", "true").json(hdfs_data_path)

# 이미지와 컨텐츠가 모두 없는 기사는 제외
df = df.filter((col("images").isNotNull()) | (col("content").isNotNull()))

# 기사에 고유 ID 추가 (1부터 시작하도록 수정)
df = df.withColumn("article_id", monotonically_increasing_id() + 1)

# NewsArticle 데이터 추출 - authors를 JSONB로 캐스팅하고 time을 timestamp로 변환
articles_df = df.select(
    col("article_id").alias("id"),
    "category",
    "title",
    "url",
    to_json("authors").cast("string").alias("authors"),
    to_timestamp("time").alias("time")
)

# NewsImage 데이터 추출 및 변환
images_df = df.select(
    col("article_id"),
    explode("images").alias("image")
).select(
    monotonically_increasing_id().alias("id"),
    "article_id",
    col("image.refid").cast(IntegerType()).alias("refid"),
    col("image.src").alias("src"),
    col("image.caption").alias("caption")
).filter(col("refid").isNotNull())

# NewsContent 데이터 추출 및 변환
content_df = df.select(
    col("article_id"),
    explode("content").alias("content")
).select(
    monotonically_increasing_id().alias("id"),
    "article_id",
    col("content.refid").cast(IntegerType()).alias("refid"),
    col("content.text").alias("text")
).filter(col("refid").isNotNull())

# 데이터 검증을 위한 로깅 추가
print("\nArticles DataFrame Schema:")
articles_df.printSchema()
print("\nSample articles data:")
articles_df.show(5, truncate=False)

print("\nImages DataFrame Schema:")
images_df.printSchema()
print("\nSample images data:")
images_df.show(5, truncate=False)

print("\nContent DataFrame Schema:")
content_df.printSchema()
print("\nSample content data:")
content_df.show(5, truncate=False)

# 데이터 저장 전 카운트 출력
print(f"\nTotal counts:")
print(f"Articles: {articles_df.count()}")
print(f"Images: {images_df.count()}")
print(f"Contents: {content_df.count()}")

# PostgreSQL에 데이터 저장
# 먼저 참조하는 테이블들의 데이터를 삭제
try:
    # 수동으로 참조하는 테이블들의 데이터를 먼저 삭제
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')
    with engine.connect() as conn:
        # 트랜잭션 시작
        with conn.begin():
            # CASCADE 옵션을 사용하여 관련된 모든 데이터 삭제
            conn.execute(text("TRUNCATE TABLE news_comment, news_newscontent, news_newsimage, news_newsarticle CASCADE"))
    print("Successfully cleared existing data")
except Exception as e:
    print("Error clearing existing data:", str(e))
    raise

# 기사 데이터 저장
try:
    articles_df.write \
        .format("jdbc") \
        .option("url", db_url) \
        .option("dbtable", "news_newsarticle") \
        .option("user", db_user) \
        .option("password", db_password) \
        .option("stringtype", "unspecified") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()
    print("Articles saved successfully")
except Exception as e:
    print(f"Error saving articles: {str(e)}")
    print(f"Current db_url: {db_url}")  # DB 연결 정보 출력 (비밀번호 제외)
    raise

# 이미지 데이터 저장 (이미지가 있을 때만)
images_count = images_df.count()
if images_count > 0:
    try:
        print(f"\nSaving {images_count} images...")
        images_df.write \
            .format("jdbc") \
            .option("url", db_url) \
            .option("dbtable", "news_newsimage") \
            .option("user", db_user) \
            .option("password", db_password) \
            .option("stringtype", "unspecified") \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
        print("Images saved successfully")
    except Exception as e:
        print("Error saving images:", str(e))
        raise

# 컨텐츠 데이터 저장 (컨텐츠가 있을 때만)
content_count = content_df.count()
if content_count > 0:
    try:
        print(f"\nSaving {content_count} contents...")
        content_df.write \
            .format("jdbc") \
            .option("url", db_url) \
            .option("dbtable", "news_newscontent") \
            .option("user", db_user) \
            .option("password", db_password) \
            .option("stringtype", "unspecified") \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
        print("Contents saved successfully")
    except Exception as e:
        print("Error saving contents:", str(e))
        raise

# 작업 종료
spark.stop()
