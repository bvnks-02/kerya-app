"""
Main FastAPI application for User Service.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

from .config import settings
from .database import init_db, close_db
from .routes import auth, users, health
from .middleware import RequestLoggingMiddleware, RateLimitMiddleware
from .utils import LoggingUtils, MetricsUtils

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting User Service", version=settings.app_version)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis connection
    from .cache import init_redis
    await init_redis()
    logger.info("Redis cache initialized")
    
    # Initialize RabbitMQ connection
    from .messaging import init_rabbitmq
    await init_rabbitmq()
    logger.info("RabbitMQ connection initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down User Service")
    await close_db()
    logger.info("User Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Kerya User Service",
    description="Authentication and User Management Service for Kerya App",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(health.router, prefix="/health", tags=["Health"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}")
    request.state.request_id = request_id
    
    # Log request
    LoggingUtils.log_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        user_id=None  # Will be set by auth middleware if authenticated
    )
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Log response
    LoggingUtils.log_response(
        request_id=request_id,
        status_code=response.status_code,
        response_time=process_time
    )
    
    # Record metrics
    MetricsUtils.record_api_call(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        response_time=process_time
    )
    
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    LoggingUtils.log_error(
        request_id=request_id,
        error=exc,
        context={"path": request.url.path, "method": request.method}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "request_id": request_id,
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    LoggingUtils.log_error(
        request_id=request_id,
        error=exc,
        context={"path": request.url.path, "method": request.method}
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "request_id": request_id,
            "timestamp": time.time()
        }
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Kerya User Service",
        "version": settings.app_version,
        "status": "running",
        "timestamp": time.time()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/status")
async def service_status():
    """Service status endpoint."""
    return {
        "service": "user-service",
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.user_service_host,
        port=settings.user_service_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 