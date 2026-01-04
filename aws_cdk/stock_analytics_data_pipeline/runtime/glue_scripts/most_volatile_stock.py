import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, stddev, log, lag, round
from pyspark.sql import Window

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_PATH', 'OUTPUT_PATH', 'DATABASE_NAME'])
input_path = args['INPUT_PATH']
output_path = args['OUTPUT_PATH']
database_name = args['DATABASE_NAME']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Minimal Glue logging
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

window = Window.partitionBy("ticker").orderBy(col("Date"))

df_returns = df.withColumn(
    "lag_close",
    lag(col("close"), 1).over(window)
).withColumn(
    "daily_return",
    log(col("close") / col("lag_close"))
).dropna()
logger.info("Calculated daily returns for each ticker")

final_df = df_returns.groupBy("ticker").agg(
    round(stddev("daily_return") * 100, 4).alias("annualized_volatility")
)
logger.info("Computed annualized volatility per ticker")

final_df.write \
    .mode("overwrite") \
    .format("parquet") \
    .option("path", output_path) \
    .saveAsTable(f"{database_name}.most_volatile_stock")

logger.info(f"Data written to {database_name}.most_volatile_stock")
logger.info(f"Job {args['JOB_NAME']} completed successfully")