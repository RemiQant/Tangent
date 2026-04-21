from fastapi import FastAPI
from app.api import api_router
from app.ml import lifespan
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import setup_limiter

def create_app() -> FastAPI:
    app = FastAPI(
        title="Music ML Microservice",
        lifespan=lifespan
    )

    setup_cors(app)
    setup_limiter(app)

    app.include_router(api_router)
    return app
