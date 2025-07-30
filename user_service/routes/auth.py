"""
Authentication routes for User Service.
"""

import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from ..config import settings
from ..database import get_db
from ..models import (
    UserCreateRequest, UserLoginRequest, AuthResponse, TokenRefreshRequest,
    TokenRefreshResponse, UserResponse, VerificationResponse
)
from ..services.auth_service import AuthService
from ..services.user_service import UserService
from ..services.cache_service import CacheService
from ..services.rate_limit_service import RateLimitService
from ..utils import LoggingUtils, MetricsUtils, ResponseUtils
from shared.models import User

logger = structlog.get_logger()
router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a new user account with email and phone verification.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        # Check rate limiting
        rate_limiter = RateLimitService()
        if not await rate_limiter.check_rate_limit(f"register:{request.client.host}", 3, 300):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many registration attempts. Please try again later."
            )
        
        # Initialize services
        auth_service = AuthService(db)
        user_service = UserService(db)
        cache_service = CacheService()
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        existing_user = await user_service.get_user_by_phone(user_data.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists"
            )
        
        # Create user
        user = await user_service.create_user(user_data)
        
        # Award registration bonus points
        await user_service.add_points(user.id, settings.points_registration_bonus, "Registration bonus")
        
        # Generate tokens
        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token()
        
        # Store session
        await auth_service.store_session(user.id, refresh_token, request.client.host, request.headers.get("user-agent"))
        
        # Send verification emails/SMS
        await auth_service.send_verification_email(user)
        await auth_service.send_verification_sms(user)
        
        # Log successful registration
        LoggingUtils.log_business_event(
            event_type="user_registered",
            user_id=user.id,
            details={"email": user.email, "user_type": user.user_type.value}
        )
        
        # Record metrics
        MetricsUtils.record_business_metric("user_registrations", 1)
        
        response_data = AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )
        
        logger.info(
            "User registered successfully",
            user_id=user.id,
            email=user.email,
            request_id=request_id,
            duration=time.time() - start_time
        )
        
        return ResponseUtils.create_success_response(
            data=response_data,
            message="User registered successfully. Please verify your email and phone number."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Registration failed",
            error=str(e),
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access tokens.
    
    Validates user credentials and returns JWT tokens for API access.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        # Check rate limiting
        rate_limiter = RateLimitService()
        rate_limit_key = f"login:{request.client.host}:{login_data.email}"
        if not await rate_limiter.check_rate_limit(rate_limit_key, 5, 300):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )
        
        # Initialize services
        auth_service = AuthService(db)
        user_service = UserService(db)
        
        # Authenticate user
        user = await auth_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            # Record failed login attempt
            await auth_service.record_failed_login(login_data.email, request.client.host, request.headers.get("user-agent"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is locked
        if await auth_service.is_account_locked(user.id):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to too many failed login attempts"
            )
        
        # Generate tokens
        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token()
        
        # Store session
        await auth_service.store_session(user.id, refresh_token, request.client.host, request.headers.get("user-agent"))
        
        # Update last login
        await user_service.update_last_login(user.id)
        
        # Log successful login
        LoggingUtils.log_business_event(
            event_type="user_login",
            user_id=user.id,
            details={"email": user.email, "ip": request.client.host}
        )
        
        # Record metrics
        MetricsUtils.record_business_metric("user_logins", 1)
        
        response_data = AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )
        
        logger.info(
            "User logged in successfully",
            user_id=user.id,
            email=user.email,
            request_id=request_id,
            duration=time.time() - start_time
        )
        
        return ResponseUtils.create_success_response(
            data=response_data,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Login failed",
            error=str(e),
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: Request,
    refresh_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Validates refresh token and returns new access and refresh tokens.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        auth_service = AuthService(db)
        
        # Validate refresh token
        session = await auth_service.validate_refresh_token(refresh_data.refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new tokens
        access_token = auth_service.create_access_token(session.user_id)
        new_refresh_token = auth_service.create_refresh_token()
        
        # Update session
        await auth_service.update_session(session.session_id, new_refresh_token)
        
        response_data = TokenRefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
        
        logger.info(
            "Token refreshed successfully",
            user_id=session.user_id,
            request_id=request_id,
            duration=time.time() - start_time
        )
        
        return ResponseUtils.create_success_response(
            data=response_data,
            message="Token refreshed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Token refresh failed",
            error=str(e),
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please try again."
        )


@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user and invalidate tokens.
    
    Invalidates the current session and refresh token.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        auth_service = AuthService(db)
        
        # Extract user ID from token
        user_id = auth_service.get_user_id_from_token(credentials.credentials)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        # Invalidate session
        await auth_service.invalidate_session(user_id, request.headers.get("user-agent"))
        
        logger.info(
            "User logged out successfully",
            user_id=user_id,
            request_id=request_id,
            duration=time.time() - start_time
        )
        
        return ResponseUtils.create_success_response(
            message="Logged out successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Logout failed",
            error=str(e),
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again."
        )


@router.post("/verify-email", response_model=VerificationResponse)
async def verify_email(
    request: Request,
    verification_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user email address.
    
    Validates email verification token and marks email as verified.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        auth_service = AuthService(db)
        
        # Verify email token
        success = await auth_service.verify_email_token(
            verification_data["email"],
            verification_data["token"]
        )
        
        if success:
            logger.info(
                "Email verified successfully",
                email=verification_data["email"],
                request_id=request_id,
                duration=time.time() - start_time
            )
            
            return ResponseUtils.create_success_response(
                message="Email verified successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Email verification failed",
            error=str(e),
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again."
        )


@router.post("/verify-phone", response_model=VerificationResponse)
async def verify_phone(
    request: Request,
    verification_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user phone number.
    
    Validates SMS verification token and marks phone as verified.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        auth_service = AuthService(db)
        
        # Verify phone token
        success = await auth_service.verify_phone_token(
            verification_data["phone"],
            verification_data["token"]
        )
        
        if success:
            logger.info(
                "Phone verified successfully",
                phone=verification_data["phone"],
                request_id=request_id,
                duration=time.time() - start_time
            )
            
            return ResponseUtils.create_success_response(
                message="Phone number verified successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Phone verification failed",
            error=str(e),
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Phone verification failed. Please try again."
        )


@router.post("/resend-verification")
async def resend_verification(
    request: Request,
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend verification email/SMS.
    
    Sends new verification tokens to user's email and phone.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        # Check rate limiting
        rate_limiter = RateLimitService()
        if not await rate_limiter.check_rate_limit(f"resend_verification:{request.client.host}", 3, 300):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many verification resend attempts. Please try again later."
            )
        
        auth_service = AuthService(db)
        user_service = UserService(db)
        
        # Get user
        user = await user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Resend verification
        await auth_service.send_verification_email(user)
        await auth_service.send_verification_sms(user)
        
        logger.info(
            "Verification resent successfully",
            email=email,
            request_id=request_id,
            duration=time.time() - start_time
        )
        
        return ResponseUtils.create_success_response(
            message="Verification codes sent successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Verification resend failed",
            error=str(e),
            request_id=request_id,
            duration=time.time() - start_time
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification. Please try again."
        ) 