from fastapi import APIRouter, HTTPException
from application.services import AthenaService
from domain.models import AthenaQuery
from core.exceptions import ErrorRequest, ErrorController

router = APIRouter()

@router.post("/execute_query")
async def execute_query(query: AthenaQuery):
    try:
        athena_service = AthenaService()
        query_execution_id = await athena_service.execute_query(query)
        return {"query_execution_id": query_execution_id}
    except ErrorRequest as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ErrorController as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_query_results/{query_execution_id}")
async def get_query_results(query_execution_id: str):
    try:
        athena_service = AthenaService()
        query_execution_id = query_execution_id.strip()  # Asegurarse de que no haya espacios en blanco ni nuevas líneas
        results = await athena_service.get_query_results(query_execution_id)
        
        # Formatear los resultados para que se vean más ordenados
        formatted_results = format_athena_results(results)
        
        return formatted_results
    except ErrorRequest as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ErrorController as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def format_athena_results(results):
    column_info = results["ResultSetMetadata"]["ColumnInfo"]
    columns = [col["Name"] for col in column_info]
    
    rows = []
    for row in results["Rows"][1:]:  # Excluir el primer elemento si es cabecera
        data = row["Data"]
        row_data = {}
        for col, value in zip(columns, data):
            row_data[col] = value.get("VarCharValue", None)
        rows.append(row_data)
    
    return {"data": rows}
