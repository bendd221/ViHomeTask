import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, avg

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_PATH', 'OUTPUT_PATH', 'DATABASE_NAME'])
input_path = args['INPUT_PATH']
output_path = args['OUTPUT_PATH']
database_name = args['DATABASE_NAME']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

logger = glueContext.get_logger()
logger.info(f"Job {args['JOB_NAME']} started")
logger.info(f"Input path: {input_path}, Output path: {output_path}, Database: {database_name}")

def load_and_preprocess(spark_session, input_path):
    logger.info("Loading input CSV")
    df = spark_session.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(input_path)
    logger.info(f"Loaded {df.count()} rows")
    return df

df = load_and_preprocess(spark, input_path)

df_traded_value = df.withColumn("traded_value", col("close") * col("volume"))
logger.info("Calculated traded value for each row")

df_daily_avg = df_traded_value.groupBy("Date").agg(
    avg("traded_value").alias("average_traded_value")
)
logger.info("Aggregated daily average traded value")

highest_value_day_df = df_daily_avg.orderBy(
    col("average_traded_value").desc()
).limit(1)
logger.info("Selected the highest average traded value day")

final_df = highest_value_day_df.select("Date", "average_traded_value").withColumnRenamed("Date", "date")

final_df.coalesce(1).write \
    .mode("overwrite") \
    .format("parquet") \
    .option("path", output_path) \
    .saveAsTable(f"{database_name}.highest_average_traded_value")

logger.info(f"Data written to {database_name}.highest_average_traded_value")
logger.info(f"Job {args['JOB_NAME']} completed successfully")