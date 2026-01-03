from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
)
from constructs import Construct
from common.props import ApiProps

class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, props: ApiProps, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        vpc = ec2.Vpc(self, "ApiVpc", max_azs=2)

        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "StocksAnalyticsApi",
            cluster=ecs.Cluster(self, "ApiCluster", vpc=vpc),
            cpu=256,
            listener_port=8000,            
            memory_limit_mib=512,

            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(props.api_app_path),
                container_port=8000,
                environment={
                    "athena_database": props.athena_database,
                    "athena_output_location": props.athena_output_location,
                },

            ),
            public_load_balancer=True,
        )

        self.service.task_definition.task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAthenaFullAccess")
        )


        self.service.load_balancer.connections.allow_from_any_ipv4(
            ec2.Port.tcp(8000),
            "Allow access to the application port 8000"
        )

        s3_bucket = s3.Bucket.from_bucket_name(self, "ApiDataBucket", props.athena_data_bucket)
        s3_bucket.grant_read_write(self.service.task_definition.task_role)
