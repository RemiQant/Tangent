import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BaseAppException

logger = logging.getLogger("uvicorn.error")

async def app_exception_handler(request: Request, exc: BaseAppException):
    logger.error("%s: %s", exc.code, exc)

    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": str(exc)}
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("INTERNAL_ERROR: %s", exc)

    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "An unexpected server error occurred."}
    )
