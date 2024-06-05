from fastapi import FastAPI, HTTPException
from typing import Union
import boto3
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from tempfile import TemporaryFile
import os

app = FastAPI()
s3 = boto3.client('s3')

S3_BUCKET = os.getenv("S3_BUCKET")

@app.post("/generate_file")
def generate_file(file_type: str, file_name: str, data: Union[dict, list]):
    if not S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")
    
    if file_type == 'excel':
        df = pd.DataFrame(data)
        with TemporaryFile() as tmp:
            df.to_excel(tmp, index=False)
            tmp.seek(0)
            s3.upload_fileobj(tmp, S3_BUCKET, file_name)
    elif file_type == 'parquet':
        table = pa.Table.from_pandas(pd.DataFrame(data))
        with TemporaryFile() as tmp:
            pq.write_table(table, tmp)
            tmp.seek(0)
            s3.upload_fileobj(tmp, S3_BUCKET, file_name)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    return {"message": f"{file_type.capitalize()} file generated successfully and uploaded to {S3_BUCKET}/{file_name}"}
