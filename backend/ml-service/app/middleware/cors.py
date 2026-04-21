import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI) -> None:
    allowed_origins = [
        o.strip()
        for o in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000"
        ).split(",")
        if o.strip()
    ]

    app.add_middleware(
    CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["POST","OPTIONS"],
        allow_headers=["Authoriation","Content-Type","X-Requested-With"],
        max_age=600
    )