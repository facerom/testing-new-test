from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as secretsmanager

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

        # File Service Lambda
        file_service_lambda = _lambda.Function(self, "FileServiceHandler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambda/file_service"),
            handler="main.lambda_handler",
            role=lambda_role,
            environment={
                "S3_BUCKET": secret.secret_value_from_json("S3_BUCKET").to_string(),
                "SECRET_KEY": secret.secret_value_from_json("SECRET_KEY").to_string()
            }
        )

        # API Gateway for File Service Lambda
        file_service_api = apigw.LambdaRestApi(self, "FileServiceEndpoint",
            handler=file_service_lambda
        )

        # Orchestration Service Lambda
        orchestration_service_lambda = _lambda.Function(self, "OrchestrationServiceHandler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambda/orchestration_service"),
            handler="main.lambda_handler",
            role=lambda_role,
            environment={
                "S3_BUCKET": secret.secret_value_from_json("S3_BUCKET").to_string(),
                "SECRET_KEY": secret.secret_value_from_json("SECRET_KEY").to_string(),
                "FILE_SERVICE_URL": "http://file-service-url"
            }
        )

        # API Gateway for Orchestration Service Lambda
        orchestration_service_api = apigw.LambdaRestApi(self, "OrchestrationServiceEndpoint",
            handler=orchestration_service_lambda
        )

        # Athena Service Lambda
        athena_service_lambda = _lambda.Function(self, "AthenaServiceHandler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambda/athena_service"),
            handler="main.lambda_handler",
            role=lambda_role,
            environment={
                "ATHENA_OUTPUT_LOCATION": "s3://your-athena-output-bucket/"
            }
        )

        # API Gateway for Athena Service Lambda
        athena_service_api = apigw.LambdaRestApi(self, "AthenaServiceEndpoint",
            handler=athena_service_lambda
        )
