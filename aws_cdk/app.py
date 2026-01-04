import json
from loguru import logger
from pathlib import Path
from aws_cdk import App
from stock_analytics_data_pipeline.infrastructure.data_infrastructure_stack import DataInfrastructureStack #Can be shortened using __init__.py
from stock_analytics_api.api_infrastructure import ApiStack
from common.props import DataPipelineProps, ApiProps
from common.config_mapper import GlueJobConfig

GLUE_JOBS_CONFIG_FILE = 'stock_analytics_data_pipeline/infrastructure/config/jobs_config.json'
BUCKET_NAME = "data-engineer-assignment-ben-dadon"
DATABASE_NAME = "assignment_ben"
LOCAL_INPUT_DATA='stock_analytics_data_pipeline/local_source_data/'

app = App()

logger.info('Starting prop initialization')
logger.debug('Loading jobs config')
with open(GLUE_JOBS_CONFIG_FILE, "r") as config_jobs:
    job_config_dict = json.load(config_jobs)

logger.debug('Constructing DataPipelineProps')
data_pipeline_props = DataPipelineProps(
    bucket_name=BUCKET_NAME,
    database_name=DATABASE_NAME,
    local_input_data=LOCAL_INPUT_DATA,
    s3_input_prefix='raw-input/stock_data/',
    glue_jobs_script_folder_path='stock_analytics_data_pipeline/runtime/glue_scripts/',
    glue_config_data=[GlueJobConfig.model_validate(job) for job in job_config_dict],
)

logger.debug('Constructing ApiProps')
api_props = ApiProps(
    athena_data_bucket=BUCKET_NAME,    
    athena_database=DATABASE_NAME,
    athena_output_location=f's3://{BUCKET_NAME}/athena_results/',
    api_app_path= "../api/app",
)
logger.info('Finished prop initialization')
DataInfrastructureStack(app, "StockAnalyticsPipelineStack", data_pipeline_props)
ApiStack(app, "StockAnalyticsAPIStack", api_props)
app.synth()