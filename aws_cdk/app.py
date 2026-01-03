import os
import json
from pathlib import Path
from aws_cdk import App
from stock_analytics_data_pipeline.infrastructure.data_infrastructure_stack import DataInfrastructureStack #Can be shortened using __init__.py
from stock_analytics_api.api_infrastructure import FastAPIStack
from common.props import DataPipelineProps, ApiProps
from common.config_mapper import GlueJobConfig

GLUE_JOBS_CONFIG_FILE = 'stock_analytics_data_pipeline/infrastructure/config/jobs_config.json'
BUCKET_NAME = "data-engineer-assignment-ben-dadon"

app = App()

with open(GLUE_JOBS_CONFIG_FILE, "r") as config_jobs:
    job_config_dict = json.load(config_jobs)

data_pipeline_props = DataPipelineProps(
    bucket_name=BUCKET_NAME,
    local_input_data='stock_analytics_data_pipeline/local_source_data/',
    s3_input_prefix='raw-input/stock_data/',
    glue_jobs_script_folder_path='stock_analytics_data_pipeline/runtime/glue_scripts/',
    glue_config_data=[GlueJobConfig.model_validate(job) for job in job_config_dict]
)

api_props = ApiProps(
    athena_database='assignment-ben',
    athena_output_location=f's3://{BUCKET_NAME}/athena_results/',
    api_app_path= "../api/app",
    athena_data_bucket=BUCKET_NAME
)

DataInfrastructureStack(app, "StockAnalyticsPipelineStack", data_pipeline_props)
FastAPIStack(app, "StockAnalyticsAPIStack", api_props)
app.synth()