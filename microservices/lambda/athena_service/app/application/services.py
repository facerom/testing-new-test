import boto3
import os
from domain.models import AthenaQuery
from infrastructure.secret_manager import SecretManagerAWS
import asyncio
from botocore.exceptions import ClientError

class AthenaService:
    def __init__(self):
        self.secret_manager = SecretManagerAWS()
        secret_name = os.getenv("SECRET_TOTTO")
        connection_secrets = self.secret_manager.get_secret(secret_name)
        self.athena = boto3.client(
            'athena', 
            aws_access_key_id=connection_secrets['accessKey'],
            aws_secret_access_key=connection_secrets['secretKey'],
        )
        self.output_location = os.getenv("ATHENA_OUTPUT_LOCATION")

    async def execute_query(self, query: AthenaQuery):
        if not self.output_location:
            raise ValueError("ATHENA_OUTPUT_LOCATION not configured")
        
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(None, lambda: self.athena.start_query_execution(
                QueryString=query.query,
                QueryExecutionContext={'Database': query.database},
                ResultConfiguration={'OutputLocation': self.output_location}
            ))
            return response['QueryExecutionId']
        except ClientError as e:
            raise Exception(f"Error executing query: {e}")

    async def get_query_results(self, query_execution_id: str):
        query_execution_id = query_execution_id.strip()  # Eliminar espacios en blanco y nuevas líneas
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(None, lambda: self.athena.get_query_results(
                QueryExecutionId=query_execution_id
            ))
            return response['ResultSet']
        except ClientError as e:
            raise Exception(f"Error getting query results: {e}")
