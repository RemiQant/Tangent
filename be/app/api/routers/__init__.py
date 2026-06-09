from fastapi import APIRouter
from app.api.routers.generate_songs import router as generate_songs_router
from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.api.routers.playlists import router as playlists_router
from app.api.routers.search import router as search_router

public_router = APIRouter()

public_router.include_router(auth_router)
public_router.include_router(users_router)
public_router.include_router(generate_songs_router, prefix="/recommendations")
public_router.include_router(playlists_router)
public_router.include_router(search_router, prefix="/search")
