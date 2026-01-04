from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
)
from loguru import logger
from constructs import Construct
from common.props import ApiProps

class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, props: ApiProps, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        logger.info('Starting ApiStack Build')
        logger.debug('Initializing a new VPC')
        vpc = ec2.Vpc(self, "ApiVpc", max_azs=2)

        logger.debug('Creating an ECS Application')
        self.service: ecs_patterns.ApplicationLoadBalancedFargateService = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "StocksAnalyticsApi",
            cluster=ecs.Cluster(self, "ApiCluster", vpc=vpc),
            cpu=256,
            listener_port=80,            
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

        logger.debug('Configuring ALB health check path to /health')
        self.service.target_group.configure_health_check(
            path="/health"
        )

        logger.debug('Adding Athena + S3 Permissions to ECS TaskRole')
        self.service.task_definition.task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAthenaFullAccess")
        )

        s3_bucket = s3.Bucket.from_bucket_name(self, "ApiDataBucket", props.athena_data_bucket)
        s3_bucket.grant_read_write(self.service.task_definition.task_role)

        logger.info("ApiStack build finished successfully")
        CfnOutput(self, "LoadBalancerDNS",
            value=self.service.load_balancer.load_balancer_dns_name,
            description=f"Use this URL for API requests. (e.g. http://load_balancer_dns/most_volatile)"
        )