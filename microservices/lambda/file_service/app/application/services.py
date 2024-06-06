import boto3
import os
from domain.models import FileRequest
from infrastructure.secret_manager import SecretManagerAWS
from botocore.exceptions import ClientError

class FileService:
    def __init__(self):
        self.secret_manager = SecretManagerAWS()
        secret_name = os.getenv("SECRET_TOTTO")
        connection_secrets = self.secret_manager.get_secret(secret_name)
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=connection_secrets['accessKey'],
            aws_secret_access_key=connection_secrets['secretKey'],
        )
        self.bucket_name = os.getenv("S3_BUCKET")

    def generate_file(self, file_request: FileRequest):
        # Implementar lógica para generar archivo
        pass
