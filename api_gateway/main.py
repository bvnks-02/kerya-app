"""
Main FastAPI application for API Gateway.
"""

import time
import httpx
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

from .config import settings
from .middleware import RequestLoggingMiddleware, RateLimitMiddleware, AuthMiddleware
from .services.gateway_service import GatewayService
from .utils import LoggingUtils, MetricsUtils, ResponseUtils

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
REQUEST_COUNT = Counter('gateway_requests_total', 'Total gateway requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('gateway_request_duration_seconds', 'Gateway request latency')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting API Gateway", version=settings.app_version)
    
    # Initialize gateway service
    gateway_service = GatewayService()
    await gateway_service.initialize()
    logger.info("Gateway service initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway")
    await gateway_service.cleanup()
    logger.info("API Gateway shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Kerya API Gateway",
    description="Central API Gateway for Kerya App microservices",
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
app.add_middleware(AuthMiddleware)

# Initialize gateway service
gateway_service = GatewayService()


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
        "service": "Kerya API Gateway",
        "version": settings.app_version,
        "status": "running",
        "timestamp": time.time()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return StreamingResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "service": "api-gateway",
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time()
    }


@app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(request: Request, path: str):
    """
    Proxy requests to appropriate microservices.
    
    Routes requests based on path patterns to the correct service.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        # Determine target service based on path
        target_service = gateway_service.get_target_service(path)
        if not target_service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Check if service is healthy
        if not await gateway_service.is_service_healthy(target_service):
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        # Forward request to target service
        response = await gateway_service.forward_request(
            request=request,
            target_service=target_service,
            path=path
        )
        
        logger.info(
            "Request forwarded successfully",
            target_service=target_service,
            path=path,
            request_id=request_id,
            duration=time.time() - start_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Request forwarding failed",
            error=str(e),
            path=path,
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=500,
            detail="Request forwarding failed"
        )


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint showing all services."""
    try:
        services_status = await gateway_service.get_services_status()
        return ResponseUtils.create_success_response(
            data=services_status,
            message="API Gateway status"
        )
    except Exception as e:
        logger.error("Failed to get services status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get services status"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_gateway_host,
        port=settings.api_gateway_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 