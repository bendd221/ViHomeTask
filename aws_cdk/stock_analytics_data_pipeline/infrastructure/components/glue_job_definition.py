from aws_cdk import (
aws_glue as glue,
aws_iam as iam,
aws_s3 as s3
)
from aws_cdk.aws_s3_assets import Asset
from dataclasses import dataclass
from typing import Optional
from constructs import Construct
from ...constants import GLUE_VERSION, GLUE_JOBS_TOP_LEVEL_PREFIX

@dataclass
class GlueJobProps:
    job_name: str
    script_path: str
    output_prefix: str
    input_path: str
    data_bucket: s3.IBucket
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

        full_output_prefix = f"{GLUE_JOBS_TOP_LEVEL_PREFIX}/{props.output_prefix.strip('/')}"

        self.script_asset.grant_read(self.glue_job_role)
        props.data_bucket.grant_read(self.glue_job_role)
        props.data_bucket.grant_read_write(self.glue_job_role, f"{full_output_prefix}/*")

        full_output_path_arg = f"s3a://{props.data_bucket.bucket_name}/{full_output_prefix}/"

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
                "--input_path": props.input_path,
                "--output_path": full_output_path_arg 
            },
            worker_type=props.worker_type,
            number_of_workers=props.number_of_workers,
            glue_version=GLUE_VERSION,
        )

        



