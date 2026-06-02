from fastapi import APIRouter
from app.api.internal.health import router as health_router

internal_router = APIRouter(prefix="/internal", tags=["Internal Infrastructure"])

internal_router.include_router(health_router)
