import json
from pathlib import Path
from dataclasses import dataclass
from common.config_mapper import GlueJobConfig
from typing import Optional
import aws_cdk.aws_s3 as s3

@dataclass(frozen=True)
class DataPipelineProps:
    bucket_name: str
    local_input_data: str
    s3_input_prefix: str
    glue_jobs_script_folder_path: str
    database_name: str
    glue_config_data: list[GlueJobConfig]

@dataclass(frozen=True)
class ApiProps:
    athena_database: str
    api_app_path: str
    athena_output_location: str
    athena_data_bucket: str
    cpu: int = 256
    memory_limit_mib: int = 512
    container_port: int = 8000