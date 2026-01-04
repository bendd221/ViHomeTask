import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext

from pyspark.sql.functions import col, avg
from pyspark.sql import Window

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_PATH', 'OUTPUT_PATH', 'DATABASE_NAME'])
input_path = args['INPUT_PATH']
output_path = args['OUTPUT_PATH']
database_name = args['DATABASE_NAME']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

def load_and_preprocess(spark_session, input_path):
    df = spark_session.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)
    return df

df = load_and_preprocess(spark, input_path)

df_traded_value = df.withColumn("traded_value", col("close") * col("volume"))

df_daily_avg = df_traded_value.groupBy("Date").agg(
    avg("traded_value").alias("average_traded_value")
)

highest_value_day_df = df_daily_avg.orderBy(
    col("average_traded_value").desc()
).limit(1)

final_df = highest_value_day_df.select("Date", "average_traded_value").withColumnRenamed("Date", "date")

final_df.coalesce(1).write \
    .mode("overwrite") \
    .format("parquet") \
    .option("path", output_path) \
    .saveAsTable(f"{database_name}.highest_average_traded_value")

