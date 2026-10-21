import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger("api_logger")


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "La solicitud no pudo completarse."
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"location": error.get("loc", []), "message": error.get("msg", "Dato no válido.")}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled %s for %s %s", type(exc).__name__, request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno. Intenta de nuevo más tarde."},
    )


def http_error(status_code: int, detail: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=detail)
