import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext

from pyspark.sql.functions import col, avg
from pyspark.sql import Window

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])
input_path = args['input_path']
output_path = args['output_path']

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
final_df.coalesce(1).write.mode("overwrite").parquet(output_path)