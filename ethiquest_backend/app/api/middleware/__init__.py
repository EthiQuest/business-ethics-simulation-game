from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from typing import Callable
import uuid

from .error_handler import error_handler, APIError
from ...config import Settings, get_settings

logger = logging.getLogger(__name__)

def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """Setup all middleware for the application"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Timing middleware
    @app.middleware("http")
    async def add_process_time(request: Request, call_next: Callable):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Error handling middleware
    @app.middleware("http")
    async def error_handling_middleware(request: Request, call_next: Callable):
        try:
            return await call_next(request)
        except Exception as exc:
            return await error_handler.handle_error(request, exc)

    # Logging middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: Callable):
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            logger.info(
                f"Response: {response.status_code}",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "status_code": response.status_code,
                    "process_time": response.headers.get("X-Process-Time")
                }
            )
            
            return response
            
        except Exception as exc:
            logger.error(
                f"Error: {str(exc)}",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "error_type": exc.__class__.__name__
                }
            )
            raise

    # Rate limiting middleware (if enabled)
    if settings.RATE_LIMIT_ENABLED:
        from .rate_limit import RateLimitMiddleware
        app.add_middleware(
            RateLimitMiddleware,
            limit=settings.RATE_LIMIT_PER_MINUTE,
            window=60
        )

    logger.info("All middleware configured successfully")