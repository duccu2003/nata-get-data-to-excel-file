from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

def setup_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.debug(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        if "Access-Control-Allow-Origin" in response.headers:
            logger.debug(f"Access-Control-Allow-Origin: {response.headers['Access-Control-Allow-Origin']}")
        return response