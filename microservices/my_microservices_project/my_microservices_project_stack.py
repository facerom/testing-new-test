from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_ecr_assets as ecr_assets,
    Duration
)
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode

class MyMicroservicesProjectStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Crear un secreto en AWS Secrets Manager
        secret = secretsmanager.Secret(self, "Secret",
            description="This secret contains the S3 bucket name and other secrets",
            secret_name="my_project_secrets",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"S3_BUCKET":"my-bucket-name"}',
                generate_string_key="SECRET_KEY"
            )
        )

        # Lambda roles
        lambda_role = iam.Role(self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAthenaFullAccess")
            ]
        )

        # File Service Lambda using Docker Image
        file_service_docker_image = DockerImageCode.from_image_asset("lambda/file_service")
        
        file_service_lambda = DockerImageFunction(self, "FileServiceHandler",
            code=file_service_docker_image,
            role=lambda_role,
            timeout=Duration.seconds(900),
            environment={
                "S3_BUCKET": secret.secret_value_from_json("S3_BUCKET").to_string()
            }
        )

        # API Gateway for File Service Lambda
        file_service_api = apigw.LambdaRestApi(self, "FileServiceEndpoint",
            handler=file_service_lambda
        )

        # Orchestration Service Lambda using Docker Image
        orchestration_service_docker_image = DockerImageCode.from_image_asset("lambda/orchestration_service")
        
        orchestration_service_lambda = DockerImageFunction(self, "OrchestrationServiceHandler",
            code=orchestration_service_docker_image,
            role=lambda_role,
            timeout=Duration.seconds(900),
            environment={
                "FILE_SERVICE_URL": file_service_api.url,
                "ATHENA_SERVICE_URL": "http://athena-service-url"
            }
        )

        # API Gateway for Orchestration Service Lambda
        orchestration_service_api = apigw.LambdaRestApi(self, "OrchestrationServiceEndpoint",
            handler=orchestration_service_lambda
        )

        # Athena Service Lambda using Docker Image
        athena_service_docker_image = DockerImageCode.from_image_asset("lambda/athena_service")
        
        athena_service_lambda = DockerImageFunction(self, "AthenaServiceHandler",
            code=athena_service_docker_image,
            role=lambda_role,
            timeout=Duration.seconds(900),
            environment={
                "SECRET_TOTTO": "totto_data_analytics",
                "ATHENA_OUTPUT_LOCATION": "s3://aws-athena-results-nalsani/"
            }
        )

        # API Gateway for Athena Service Lambda
        athena_service_api = apigw.LambdaRestApi(self, "AthenaServiceEndpoint",
            handler=athena_service_lambda
        )

# Instantiate the stack
app = core.App()
MyMicroservicesProjectStack(app, "MyMicroservicesProjectStack")
app.synth()