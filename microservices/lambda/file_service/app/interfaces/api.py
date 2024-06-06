from fastapi import APIRouter, HTTPException, Request
from application.services import FileService
from core.exceptions import ErrorRequest, ErrorController

router = APIRouter()

@router.post("/generate_file")
async def generate_file(request: Request):
    body = await request.json()
    action = body.get("action")
    file_path = body.get("file_path", "output.xlsx")
    
    try:
        file_service = FileService()
        if action == "generate_file":
            file_service.generate_file(file_path)
            return {"message": f"File generated at {file_path}"}
        else:
            raise ErrorRequest(status_code=400, detail="No se ha especificado una acción válida")
    except ErrorRequest as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ErrorController as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
