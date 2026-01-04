from aws_cdk import (
aws_glue as glue,
aws_iam as iam,
aws_s3 as s3
)
from aws_cdk.aws_s3_assets import Asset
from dataclasses import dataclass
from typing import Optional
from constructs import Construct

@dataclass
class GlueJobProps:
    job_name: str
    database_name: str
    script_path: str
    s3_input_prefix: str
    s3_output_prefix: str
    data_bucket: s3.IBucket
    glue_version:str
    worker_type: Optional[str] = "G.1X"
    number_of_workers: Optional[int] = 2

class GlueJobDefinition(Construct):
    def __init__(self, scope: Construct, id: str, props: GlueJobProps, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.script_asset = Asset(
            self,
            id,
            path=props.script_path
        )

        self.glue_job_role = iam.Role(
            self, 
            f"Role-{id}",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
            ]
        )

        self.script_asset.grant_read(self.glue_job_role)
        props.data_bucket.grant_read(self.glue_job_role)
        props.data_bucket.grant_write(self.glue_job_role, f"{props.s3_output_prefix}/*")

        full_input_path_arg = f"s3a://{props.data_bucket.bucket_name}/{props.s3_input_prefix}"
        full_output_path_arg = f"s3a://{props.data_bucket.bucket_name}/{props.s3_output_prefix}/"

        glue.CfnJob(
            self,
            "CfnJobDefinition",
            name=props.job_name,
            role=self.glue_job_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=self.script_asset.s3_object_url,
                python_version="3"
            ),
            default_arguments={
                "--INPUT_PATH": full_input_path_arg,
                "--OUTPUT_PATH": full_output_path_arg,
                "--enable-glue-datacatalog": True,
                "--DATABASE_NAME": props.database_name
            },
            worker_type=props.worker_type,
            number_of_workers=props.number_of_workers,
            glue_version=props.glue_version,
        )

        



