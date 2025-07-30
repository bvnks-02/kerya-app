"""
User Service models and schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

from shared.models import User, UserType


class UserCreateRequest(BaseModel):
    """User registration request model."""
    email: EmailStr = Field(..., description="User email address")
    phone: str = Field(..., description="User phone number")
    password: str = Field(..., min_length=8, description="User password")
    first_name: str = Field(..., min_length=2, max_length=100, description="User first name")
    last_name: str = Field(..., min_length=2, max_length=100, description="User last name")
    user_type: UserType = Field(default=UserType.CLIENT, description="User type")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        from shared.utils import ValidationUtils
        if not ValidationUtils.validate_phone(v):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        from shared.utils import ValidationUtils
        result = ValidationUtils.validate_password_strength(v)
        if not result["valid"]:
            raise ValueError(f"Password validation failed: {', '.join(result['errors'])}")
        return v


class UserLoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserUpdateRequest(BaseModel):
    """User profile update request model."""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None)
    profile_image: Optional[str] = Field(None)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is not None:
            from shared.utils import ValidationUtils
            if not ValidationUtils.validate_phone(v):
                raise ValueError('Invalid phone number format')
        return v


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    phone: str
    first_name: str
    last_name: str
    user_type: UserType
    is_verified: bool
    profile_image: Optional[str]
    rating: float
    points: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """User profile response model."""
    id: int
    email: str
    phone: str
    first_name: str
    last_name: str
    user_type: UserType
    is_verified: bool
    profile_image: Optional[str]
    rating: float
    points: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefreshRequest(BaseModel):
    """Token refresh request model."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordChangeRequest(BaseModel):
    """Password change request model."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        from shared.utils import ValidationUtils
        result = ValidationUtils.validate_password_strength(v)
        if not result["valid"]:
            raise ValueError(f"Password validation failed: {', '.join(result['errors'])}")
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request model."""
    email: EmailStr
    token: str


class PhoneVerificationRequest(BaseModel):
    """Phone verification request model."""
    phone: str
    token: str


class VerificationResponse(BaseModel):
    """Verification response model."""
    success: bool
    message: str


class PointsResponse(BaseModel):
    """Points response model."""
    points: int
    history: list


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    user_id: int
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str


class LoginAttempt(BaseModel):
    """Login attempt model."""
    email: str
    ip_address: str
    user_agent: str
    success: bool
    timestamp: datetime


class SecuritySettings(BaseModel):
    """Security settings model."""
    two_factor_enabled: bool = False
    email_notifications: bool = True
    sms_notifications: bool = True
    login_notifications: bool = True


class UserStats(BaseModel):
    """User statistics model."""
    total_bookings: int
    total_reviews: int
    total_points_earned: int
    total_points_spent: int
    member_since_days: int
    last_activity: datetime


# Additional models for internal use

class UserSession(BaseModel):
    """User session model for caching."""
    user_id: int
    session_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime


class VerificationToken(BaseModel):
    """Verification token model."""
    user_id: int
    token: str
    token_type: str  # email, phone, password_reset
    expires_at: datetime
    used: bool = False


class RateLimitInfo(BaseModel):
    """Rate limit information model."""
    key: str
    requests: int
    window_start: datetime
    window_end: datetime
    limit: int


class AuditLog(BaseModel):
    """Audit log model."""
    user_id: int
    action: str
    details: dict
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool 