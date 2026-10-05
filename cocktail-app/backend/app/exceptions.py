from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_logger")

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error occurred: {str(exc)} | Path: {request.url.path}")
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "status": "error"},
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "status": "critical"},
    )
