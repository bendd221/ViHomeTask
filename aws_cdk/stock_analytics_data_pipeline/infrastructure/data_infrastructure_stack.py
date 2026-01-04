import json
from loguru import logger
from aws_cdk import (
    aws_s3_deployment as s3_deployment,
    aws_s3 as s3,
    aws_glue as glue,
    RemovalPolicy,
    Stack
)

from constructs import Construct
from pathlib import Path
from common.props import DataPipelineProps
from .components.glue_job_definition import GlueJobDefinition, GlueJobProps


class DataInfrastructureStack(Stack):
    def __init__(self, scope: Construct, id: str, props: DataPipelineProps,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        logger.info('Starting DataInfrastructureStack Build')
        logger.debug('Creating S3 Bucket')
        data_bucket = s3.Bucket(self, 'DataBucket', 
            bucket_name=props.bucket_name,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.RETAIN,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        logger.debug('Uploading S3 Input Data')
        s3_deployment.BucketDeployment(self, "DeployInputData",
            sources=[s3_deployment.Source.asset(str(Path(props.local_input_data)))],
            destination_bucket=data_bucket,
            destination_key_prefix=props.s3_input_prefix,
        )

        logger.debug('Creating Glue Database')
        glue.CfnDatabase(
            self,
            "StocksGlueDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=props.database_name,
            ),
        )

        logger.debug('Creating Glue Jobs')
        for config in props.glue_config_data:
            unique_id = f"Job-{config.job_name}"
            logger.debug(unique_id)
            
            GlueJobDefinition(self, unique_id,
                props=GlueJobProps(
                    job_name=config.job_name,
                    database_name=props.database_name,
                    script_path=str(Path(props.glue_jobs_script_folder_path) / config.script_name),
                    s3_output_prefix=config.output_sub_folder,
                    data_bucket=data_bucket,
                    glue_version=config.glue_version,
                    s3_input_prefix=props.s3_input_prefix
                )
            )
        logger.info("DataInfrastructureStack build finished successfully")