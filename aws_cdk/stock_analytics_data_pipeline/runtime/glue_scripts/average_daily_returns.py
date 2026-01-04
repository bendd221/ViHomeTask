import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext

from pyspark.sql.functions import col, avg, lag, round
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

df_window = Window.partitionBy("ticker").orderBy(col("Date"))

df_returns = df.withColumn(
    "lag_close", 
    lag(col("close"), 1).over(df_window)
).withColumn(
    "daily_return", 
    (col("close") / col("lag_close")) - 1
).dropna() 

final_df = df_returns.groupBy("Date").agg(
    round(avg("daily_return") * 100, 4).alias("average_return")
).select(
    col("Date").alias("date"), 
    "average_return"
)

final_df.write \
    .mode("overwrite") \
    .format("parquet") \
    .partitionBy("date") \
    .option("path", output_path) \
    .saveAsTable(f"{database_name}.average_daily_return")