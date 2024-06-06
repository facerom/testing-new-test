from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
from dotenv import load_dotenv
import os
from application.services import OrchestrationService
from interfaces.api import router as api_router

# Cargar variables de entorno solo si se está ejecutando localmente
if os.getenv("ENVIRONMENT") != "PRODUCTION":
    load_dotenv()

app = FastAPI()

orchestration_service = OrchestrationService()
app.include_router(api_router)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})

# Handler para AWS Lambda
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
