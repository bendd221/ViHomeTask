import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import aws_cdk.aws_s3 as s3

@dataclass()
class GlueJobProps:
    job_name: str
    script_path: str
    s3_output_prefix: str
    glue_version: str
    data_bucket: Optional[s3.IBucket]
    worker_type: Optional[str] = "G.1X"
    number_of_workers: Optional[int] = 2
    glue_jobs_top_level_prefix: str

@dataclass(frozen=True)
class DataPipelineProps:
    bucket_name: str
    local_input_data: str
    s3_input_prefix: str
    glue_jobs_list: list[GlueJobProps]

@dataclass(frozen=True)
class ApiProps:
    athena_database: str
    athena_output_location: str
    cpu: int = 256
    memory_limit_mib: int = 512
    container_port: int = 8000


def generate_glue_job_config(config_path: str, script_folder_path: str):
    with open(config_path, 'r') as f:
        jobs_config = json.load(f)
        return [
            GlueJobProps(
                job_name=job_config['job_name'],
                script_path=Path(script_folder_path) / job_config['script_name'],
                s3_output_prefix=job_config['output_sub_folder'],
                glue_version=job_config['glue_version'],
                glue_jobs_top_level_prefix=job_config.get('glue_jobs_top_level_prefix', None),
            )
            for job_config in jobs_config
        ]
    