import json

from aws_cdk import (
    aws_s3_deployment as s3_deployment,
    aws_s3 as s3,
    RemovalPolicy,
    Stack
)

from constructs import Construct
from pathlib import Path
from .components.glue_job_definition import GlueJobDefinition, GlueJobProps
from ..constants import BUCKET_NAME, LOCAL_INPUT_DATA, S3_INPUT_PREFIX, GLUE_JOBS_CONFIG_FILE, GLUE_JOBS_SCRIPT_FOLDER_PATH


class DataInfrastructureStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        data_bucket = s3.Bucket(self, 'DataBucket', 
            bucket_name=BUCKET_NAME,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.RETAIN,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        s3_deployment.BucketDeployment(self, "DeployInputData",
            sources=[s3_deployment.Source.asset(str(Path(LOCAL_INPUT_DATA)))],
            destination_bucket=data_bucket,
            destination_key_prefix=S3_INPUT_PREFIX,
        )

        input_s3_uri = f"s3a://{BUCKET_NAME}/{S3_INPUT_PREFIX}"

        with open(GLUE_JOBS_CONFIG_FILE, 'r') as f:
            jobs_config = json.load(f)

        for config in jobs_config:
            unique_id = f"Job-{config['job_name']}"
            
            GlueJobDefinition(self, unique_id,
                props=GlueJobProps(
                    job_name=config['job_name'],
                    script_path=str(Path(GLUE_JOBS_SCRIPT_FOLDER_PATH) / config['script_name']),
                    output_prefix=config['output_sub_folder'],
                    data_bucket=data_bucket,
                    input_path=input_s3_uri,
                )
            )