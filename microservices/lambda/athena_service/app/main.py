from fastapi import FastAPI, HTTPException
import boto3
import os

app = FastAPI()
athena = boto3.client('athena')

ATHENA_OUTPUT_LOCATION = os.getenv("ATHENA_OUTPUT_LOCATION")

@app.post("/execute_query")
def execute_query(database: str, query: str):
    if not ATHENA_OUTPUT_LOCATION:
        raise HTTPException(status_code=500, detail="ATHENA_OUTPUT_LOCATION not configured")
    
    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_LOCATION}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"query_execution_id": response['QueryExecutionId']}

@app.get("/get_query_results")
def get_query_results(query_execution_id: str):
    try:
        response = athena.get_query_results(QueryExecutionId=query_execution_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"result": response['ResultSet']}
