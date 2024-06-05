from fastapi import FastAPI, HTTPException
import boto3
from botocore.exceptions import NoCredentialsError
import os
import requests

app = FastAPI()
s3 = boto3.client('s3')

@app.get("/generate_presigned_url")
def generate_presigned_url(object_name: str, expiration: int = 3600):
    bucket_name = os.getenv("S3_BUCKET")
    if not bucket_name:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")

    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': object_name},
                                             ExpiresIn=expiration)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Credentials not available")
    return {"url": response}

@app.post("/orchestrate_task")
def orchestrate_task(data: dict):
    # Example of orchestrating tasks between services
    file_service_url = os.getenv("FILE_SERVICE_URL")
    if not file_service_url:
        raise HTTPException(status_code=500, detail="FILE_SERVICE_URL not configured")

    response = requests.post(f"{file_service_url}/generate_file", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return {"message": "Orchestration completed successfully", "file_service_response": response.json()}

@app.post("/orchestrate_athena_query")
def orchestrate_athena_query(database: str, query: str):
    athena_service_url = os.getenv("ATHENA_SERVICE_URL")
    if not athena_service_url:
        raise HTTPException(status_code=500, detail="ATHENA_SERVICE_URL not configured")

    # Execute query
    response = requests.post(f"{athena_service_url}/execute_query", json={"database": database, "query": query})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    query_execution_id = response.json().get("query_execution_id")
    
    # Get query results
    response = requests.get(f"{athena_service_url}/get_query_results", params={"query_execution_id": query_execution_id})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return {"message": "Athena query completed successfully", "athena_results": response.json()}
