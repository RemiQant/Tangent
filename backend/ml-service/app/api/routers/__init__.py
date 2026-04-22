from fastapi import APIRouter
from app.api.routers.generate_songs import router as generate_songs_router

public_router = APIRouter()

public_router.include_router(generate_songs_router, prefix="/recommendations")
