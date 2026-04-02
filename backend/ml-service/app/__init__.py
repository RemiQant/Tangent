from fastapi import FastAPI
from app.api import api_router
from app.ml import lifespan

__all__ = ["create_app"]

def create_app() -> FastAPI:
    app = FastAPI(
        title="Music ML Microservice",
        lifespan=lifespan
    )

    app.include_router(api_router)

    return app
