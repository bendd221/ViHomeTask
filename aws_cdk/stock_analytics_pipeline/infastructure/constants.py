##General S3 Constants
BUCKET_NAME = 'data-engineer-assignment-ben-dadon'
LOCAL_INPUT_DATA = './stock_analytics_pipeline/local_source_data/'
S3_INPUT_PREFIX = 'raw-input/stock_data/'

##Glue Job Constants
GLUE_VERSION = "5.0"
GLUE_JOBS_CONFIG_FILE = './stock_analytics_pipeline/infastructure/config/jobs_config.json'
GLUE_JOBS_SCRIPT_FOLDER_PATH='./stock_analytics_pipeline/runtime/glue_scripts/'
GLUE_JOBS_TOP_LEVEL_PREFIX = 'results'