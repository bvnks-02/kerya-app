"""
Shared utility functions for Kerya App microservices.
"""

import hashlib
import json
import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import bcrypt
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from pydantic import BaseModel

from .config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


class SecurityUtils:
    """Security utility functions."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def generate_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Generate a JWT token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def generate_refresh_token() -> str:
        """Generate a refresh token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        """Encrypt sensitive data using Fernet."""
        fernet = Fernet(settings.encryption_key.encode())
        return fernet.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Decrypt sensitive data using Fernet."""
        fernet = Fernet(settings.encryption_key.encode())
        return fernet.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class ValidationUtils:
    """Validation utility functions."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        import re
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        result = {
            "valid": True,
            "errors": []
        }
        
        if len(password) < 8:
            result["valid"] = False
            result["errors"].append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            result["valid"] = False
            result["errors"].append("Password must contain at least one digit")
        
        return result


class CacheUtils:
    """Cache utility functions."""
    
    @staticmethod
    def generate_cache_key(prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    @staticmethod
    def serialize_data(data: Any) -> str:
        """Serialize data for caching."""
        if isinstance(data, BaseModel):
            return data.json()
        return json.dumps(data, default=str)
    
    @staticmethod
    def deserialize_data(data: str, model_class: Optional[type] = None) -> Any:
        """Deserialize data from cache."""
        try:
            parsed = json.loads(data)
            if model_class and issubclass(model_class, BaseModel):
                return model_class(**parsed)
            return parsed
        except (json.JSONDecodeError, TypeError):
            return data


class FileUtils:
    """File utility functions."""
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
        """Validate file type based on extension."""
        import os
        _, ext = os.path.splitext(filename.lower())
        return ext in allowed_types
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> bool:
        """Validate file size."""
        return file_size <= max_size
    
    @staticmethod
    def generate_filename(original_filename: str, prefix: str = "") -> str:
        """Generate a unique filename."""
        import os
        import uuid
        _, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())
        return f"{prefix}{unique_id}{ext}" if prefix else f"{unique_id}{ext}"
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        import os
        return os.path.splitext(filename)[1].lower()


class DateUtils:
    """Date and time utility functions."""
    
    @staticmethod
    def is_valid_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Check if date range is valid."""
        return start_date < end_date
    
    @staticmethod
    def calculate_date_difference(start_date: datetime, end_date: datetime) -> int:
        """Calculate the difference in days between two dates."""
        return (end_date - start_date).days
    
    @staticmethod
    def is_future_date(date: datetime) -> bool:
        """Check if date is in the future."""
        return date > datetime.utcnow()
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime to string."""
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        """Parse string to datetime."""
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError:
            return None


class BusinessLogicUtils:
    """Business logic utility functions."""
    
    @staticmethod
    def calculate_booking_price(price_per_night: float, check_in: datetime, check_out: datetime) -> float:
        """Calculate total booking price."""
        days = DateUtils.calculate_date_difference(check_in, check_out)
        return price_per_night * days
    
    @staticmethod
    def calculate_user_rating(ratings: List[int]) -> float:
        """Calculate average user rating."""
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)
    
    @staticmethod
    def calculate_points_earned(booking_price: float, base_points: int = 50) -> int:
        """Calculate points earned from booking."""
        # 1 point per 10 currency units
        return int(booking_price / 10) + base_points
    
    @staticmethod
    def is_booking_cancellable(booking_date: datetime, cancellation_hours: int = 24) -> bool:
        """Check if booking can be cancelled."""
        cutoff_time = booking_date - timedelta(hours=cancellation_hours)
        return datetime.utcnow() < cutoff_time
    
    @staticmethod
    def can_user_review(booking_end_date: datetime, review_days_limit: int = 14) -> bool:
        """Check if user can still review a booking."""
        review_deadline = booking_end_date + timedelta(days=review_days_limit)
        return datetime.utcnow() <= review_deadline


class ResponseUtils:
    """Response utility functions."""
    
    @staticmethod
    def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Create a standardized success response."""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def create_error_response(message: str, error_code: str = None, details: Any = None) -> Dict[str, Any]:
        """Create a standardized error response."""
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if error_code:
            response["error_code"] = error_code
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def paginate_response(data: List[Any], page: int, size: int, total: int) -> Dict[str, Any]:
        """Create a paginated response."""
        return {
            "data": data,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size,
                "has_next": page * size < total,
                "has_prev": page > 1
            }
        }


class LoggingUtils:
    """Logging utility functions."""
    
    @staticmethod
    def log_request(request_id: str, method: str, path: str, user_id: Optional[int] = None):
        """Log incoming request."""
        logger.info(f"Request {request_id}: {method} {path} - User: {user_id}")
    
    @staticmethod
    def log_response(request_id: str, status_code: int, response_time: float):
        """Log response details."""
        logger.info(f"Response {request_id}: {status_code} - {response_time:.3f}s")
    
    @staticmethod
    def log_error(request_id: str, error: Exception, context: Dict[str, Any] = None):
        """Log error with context."""
        error_data = {
            "request_id": request_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        logger.error(f"Error: {json.dumps(error_data)}")
    
    @staticmethod
    def log_business_event(event_type: str, user_id: int, details: Dict[str, Any] = None):
        """Log business events."""
        event_data = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        logger.info(f"Business Event: {json.dumps(event_data)}")


class MetricsUtils:
    """Metrics utility functions."""
    
    @staticmethod
    def record_api_call(endpoint: str, method: str, status_code: int, response_time: float):
        """Record API call metrics."""
        # This would integrate with Prometheus or other metrics system
        logger.info(f"API Call: {method} {endpoint} - {status_code} - {response_time:.3f}s")
    
    @staticmethod
    def record_business_metric(metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record business metrics."""
        # This would integrate with Prometheus or other metrics system
        metric_data = {
            "metric": metric_name,
            "value": value,
            "labels": labels or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(f"Business Metric: {json.dumps(metric_data)}")
    
    @staticmethod
    def record_error_metric(error_type: str, endpoint: str = None):
        """Record error metrics."""
        # This would integrate with Prometheus or other metrics system
        error_data = {
            "error_type": error_type,
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.error(f"Error Metric: {json.dumps(error_data)}") 