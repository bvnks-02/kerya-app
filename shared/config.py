"""
Shared configuration settings for Kerya App microservices.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = Field(default="Kerya App", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # Elasticsearch
    elasticsearch_url: str = Field(..., env="ELASTICSEARCH_URL")
    elasticsearch_username: str = Field(default="elastic", env="ELASTICSEARCH_USERNAME")
    elasticsearch_password: str = Field(default="changeme", env="ELASTICSEARCH_PASSWORD")
    elasticsearch_index_prefix: str = Field(default="kerya", env="ELASTICSEARCH_INDEX_PREFIX")
    
    # RabbitMQ
    rabbitmq_url: str = Field(..., env="RABBITMQ_URL")
    rabbitmq_host: str = Field(default="rabbitmq", env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, env="RABBITMQ_PORT")
    rabbitmq_user: str = Field(default="guest", env="RABBITMQ_USER")
    rabbitmq_password: str = Field(default="guest", env="RABBITMQ_PASSWORD")
    rabbitmq_vhost: str = Field(default="/", env="RABBITMQ_VHOST")
    
    # AWS S3
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket: str = Field(..., env="AWS_S3_BUCKET")
    aws_s3_endpoint_url: str = Field(default="https://s3.amazonaws.com", env="AWS_S3_ENDPOINT_URL")
    
    # JWT
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # OAuth 2.0
    google_client_id: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(default="http://localhost:8000/api/v1/auth/google/callback", env="GOOGLE_REDIRECT_URI")
    
    # Email (SendGrid)
    sendgrid_api_key: str = Field(..., env="SENDGRID_API_KEY")
    sendgrid_from_email: str = Field(default="noreply@kerya.com", env="SENDGRID_FROM_EMAIL")
    sendgrid_from_name: str = Field(default="Kerya App", env="SENDGRID_FROM_NAME")
    
    # SMS (Twilio)
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(..., env="TWILIO_PHONE_NUMBER")
    
    # Google Maps
    google_maps_api_key: str = Field(..., env="GOOGLE_MAPS_API_KEY")
    google_maps_base_url: str = Field(default="https://maps.googleapis.com/maps/api", env="GOOGLE_MAPS_BASE_URL")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    allowed_hosts: List[str] = Field(default=["localhost"], env="ALLOWED_HOSTS")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # File Upload
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(default=["image/jpeg", "image/png", "image/webp"], env="ALLOWED_FILE_TYPES")
    upload_dir: str = Field(default="/app/uploads", env="UPLOAD_DIR")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: str = Field(default="/app/logs/kerya.log", env="LOG_FILE")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    jaeger_enabled: bool = Field(default=True, env="JAEGER_ENABLED")
    jaeger_host: str = Field(default="jaeger", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_PORT")
    
    # Service URLs
    user_service_url: str = Field(default="http://user_service:8001", env="USER_SERVICE_URL")
    property_service_url: str = Field(default="http://property_service:8002", env="PROPERTY_SERVICE_URL")
    booking_service_url: str = Field(default="http://booking_service:8003", env="BOOKING_SERVICE_URL")
    notification_service_url: str = Field(default="http://notification_service:8004", env="NOTIFICATION_SERVICE_URL")
    review_service_url: str = Field(default="http://review_service:8005", env="REVIEW_SERVICE_URL")
    post_service_url: str = Field(default="http://post_service:8006", env="POST_SERVICE_URL")
    
    # Points System
    points_registration_bonus: int = Field(default=100, env="POINTS_REGISTRATION_BONUS")
    points_booking_earn: int = Field(default=50, env="POINTS_BOOKING_EARN")
    points_review_earn: int = Field(default=25, env="POINTS_REVIEW_EARN")
    points_post_cost: int = Field(default=10, env="POINTS_POST_COST")
    
    # Business Logic
    max_booking_days: int = Field(default=30, env="MAX_BOOKING_DAYS")
    min_booking_notice_hours: int = Field(default=2, env="MIN_BOOKING_NOTICE_HOURS")
    cancellation_policy_hours: int = Field(default=24, env="CANCELLATION_POLICY_HOURS")
    review_days_limit: int = Field(default=14, env="REVIEW_DAYS_LIMIT")
    
    # Cache
    cache_ttl: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    session_ttl: int = Field(default=3600, env="SESSION_TTL")  # 1 hour
    property_cache_ttl: int = Field(default=600, env="PROPERTY_CACHE_TTL")  # 10 minutes
    
    # Notifications
    email_notifications_enabled: bool = Field(default=True, env="EMAIL_NOTIFICATIONS_ENABLED")
    sms_notifications_enabled: bool = Field(default=True, env="SMS_NOTIFICATIONS_ENABLED")
    push_notifications_enabled: bool = Field(default=True, env="PUSH_NOTIFICATIONS_ENABLED")
    
    # Search
    elasticsearch_index_shards: int = Field(default=1, env="ELASTICSEARCH_INDEX_SHARDS")
    elasticsearch_index_replicas: int = Field(default=0, env="ELASTICSEARCH_INDEX_REPLICAS")
    search_results_limit: int = Field(default=50, env="SEARCH_RESULTS_LIMIT")
    
    # Development/Testing
    testing: bool = Field(default=False, env="TESTING")
    mock_external_services: bool = Field(default=False, env="MOCK_EXTERNAL_SERVICES")
    seed_data_enabled: bool = Field(default=True, env="SEED_DATA_ENABLED")
    
    # Health Check
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    # Backup
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_schedule: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")  # Daily at 2 AM
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    @validator("cors_origins", "allowed_hosts", pre=True)
    def parse_list_fields(cls, v):
        """Parse comma-separated strings into lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_file_types(cls, v):
        """Parse comma-separated file types into list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings 