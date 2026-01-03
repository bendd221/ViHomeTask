import os
from pathlib import Path
from aws_cdk import App
from stock_analytics_data_pipeline.infrastructure.data_infrastructure_stack import DataInfrastructureStack #Can be shortened using __init__.py
from stock_analytics_api.infrastructure import FastAPIStack
from props import DataPipelineProps, GlueJobProps, ApiProps

# PROJECT_ROOT = Path(__file__).resolve().parents[0]
GLUE_JOBS_CONFIG_FILE = 'stock_analytics_data_pipeline/infrastructure/config/jobs_config.json'
GLUE_JOBS_SCRIPT_FOLDER_PATH = 'stock_analytics_data_pipeline/runtime/glue_scripts/'

app = App()

data_pipeline_props = DataPipelineProps(
    bucket_name="data-engineer-assignment-ben-dadon",
    local_input_data='stock_analytics_data_pipeline/local_source_data/',
    s3_input_prefix='raw-input/stock_data/',
    glue_jobs_list=[]
)

api_props = ApiProps(
    athena_database='assignment-ben',
    athena_output_location='s3://data-assignment-ben-dadon/athena_results/'
)

#create glue jobs but i dont have the bucket yet then pass it
DataInfrastructureStack(app, "StockAnalyticsPipelineStack")
FastAPIStack(app, "StockAnalyticsAPIStack")
app.synth()