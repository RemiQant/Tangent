from fastapi import APIRouter
from app.api.routers import public_router
from app.api.internal import internal_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(public_router)
api_router.include_router(internal_router)
