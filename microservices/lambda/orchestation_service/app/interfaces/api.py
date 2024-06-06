# Las rutas de la API se definen en main.py
from fastapi import APIRouter, HTTPException, Request
from application.services import OrchestrationService
from core.exceptions import ErrorRequest, ErrorController

router = APIRouter()

@router.post("/orchestrate_task")
async def orchestrate_task(request: Request):
    body = await request.json()
    action = body.get("action")
    task_details = body.get("task_details", {})
    
    try:
        orchestration_service = OrchestrationService()
        if action == "orchestrate_task":
            orchestration_service.orchestrate_task(task_details)
            return {"message": "Task orchestrated successfully"}
        else:
            raise ErrorRequest(status_code=400, detail="No se ha especificado una acción válida")
    except ErrorRequest as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ErrorController as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
