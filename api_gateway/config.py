"""
Configuration settings for API Gateway.
"""

from shared.config import Settings


class APIGatewaySettings(Settings):
    """API Gateway specific settings."""
    
    # Service specific settings
    api_gateway_host: str = "0.0.0.0"
    api_gateway_port: int = 8000
    api_gateway_workers: int = 4
    
    # Load balancing settings
    load_balancer_algorithm: str = "round_robin"  # round_robin, least_connections, weighted
    health_check_interval: int = 30
    health_check_timeout: int = 5
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    
    # Rate limiting
    global_rate_limit_requests: int = 1000
    global_rate_limit_window: int = 60
    per_user_rate_limit_requests: int = 100
    per_user_rate_limit_window: int = 60
    
    # Caching
    response_cache_ttl: int = 300  # 5 minutes
    cache_enabled: bool = True
    
    # Security
    jwt_validation_enabled: bool = True
    cors_enabled: bool = True
    request_size_limit: int = 10485760  # 10MB
    
    # Monitoring
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    request_logging_enabled: bool = True
    
    # Service discovery
    service_discovery_enabled: bool = True
    service_registry_url: str = "http://service-registry:8080"
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    circuit_breaker_expected_exceptions: list = ["HTTPException", "TimeoutError"]
    
    # Retry settings
    retry_enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff_factor: float = 2.0
    
    # Timeout settings
    request_timeout: int = 30
    connect_timeout: int = 10
    read_timeout: int = 30
    
    # Logging
    access_log_enabled: bool = True
    error_log_enabled: bool = True
    log_request_body: bool = False
    log_response_body: bool = False
    
    # SSL/TLS
    ssl_enabled: bool = False
    ssl_cert_file: str = ""
    ssl_key_file: str = ""
    
    # API documentation
    docs_enabled: bool = True
    redoc_enabled: bool = True
    
    # Service routing rules
    service_routes: dict = {
        "auth": {
            "prefix": "/api/v1/auth",
            "service_url": "http://user_service:8001",
            "health_check": "/health",
            "rate_limit": {"requests": 100, "window": 60}
        },
        "users": {
            "prefix": "/api/v1/users",
            "service_url": "http://user_service:8001",
            "health_check": "/health",
            "rate_limit": {"requests": 200, "window": 60}
        },
        "properties": {
            "prefix": "/api/v1/properties",
            "service_url": "http://property_service:8002",
            "health_check": "/health",
            "rate_limit": {"requests": 300, "window": 60}
        },
        "bookings": {
            "prefix": "/api/v1/bookings",
            "service_url": "http://booking_service:8003",
            "health_check": "/health",
            "rate_limit": {"requests": 200, "window": 60}
        },
        "posts": {
            "prefix": "/api/v1/posts",
            "service_url": "http://post_service:8006",
            "health_check": "/health",
            "rate_limit": {"requests": 150, "window": 60}
        },
        "reviews": {
            "prefix": "/api/v1/reviews",
            "service_url": "http://review_service:8005",
            "health_check": "/health",
            "rate_limit": {"requests": 100, "window": 60}
        }
    }


# Global settings instance
settings = APIGatewaySettings()


def get_settings() -> APIGatewaySettings:
    """Get API Gateway settings."""
    return settings 