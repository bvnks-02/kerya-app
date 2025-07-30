"""
Configuration settings for User Service.
"""

from shared.config import Settings


class UserServiceSettings(Settings):
    """User Service specific settings."""
    
    # Service specific settings
    user_service_host: str = "0.0.0.0"
    user_service_port: int = 8001
    
    # Authentication settings
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # Email verification
    email_verification_required: bool = True
    email_verification_token_expire_hours: int = 24
    
    # Phone verification
    phone_verification_required: bool = True
    sms_verification_token_expire_minutes: int = 10
    
    # Points system
    points_registration_bonus: int = 100
    points_referral_bonus: int = 50
    points_profile_completion: int = 25
    
    # Rate limiting for auth endpoints
    auth_rate_limit_requests: int = 5
    auth_rate_limit_window: int = 300  # 5 minutes
    
    # Session management
    session_timeout_hours: int = 24
    max_concurrent_sessions: int = 3
    
    # Security
    bcrypt_rounds: int = 12
    password_history_count: int = 5
    
    # External service timeouts
    email_service_timeout: int = 10
    sms_service_timeout: int = 10
    
    # Cache settings
    user_cache_ttl: int = 3600  # 1 hour
    session_cache_ttl: int = 86400  # 24 hours
    verification_cache_ttl: int = 600  # 10 minutes


# Global settings instance
settings = UserServiceSettings()


def get_settings() -> UserServiceSettings:
    """Get User Service settings."""
    return settings 