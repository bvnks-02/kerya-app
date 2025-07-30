# Kerya App Security Documentation

## Overview

This document outlines the security measures, best practices, and protocols implemented in the Kerya App back-end to ensure data protection, user privacy, and system integrity.

## Security Architecture

### Defense in Depth

The Kerya App implements a multi-layered security approach:

1. **Network Layer**: TLS encryption, firewalls, DDoS protection
2. **Application Layer**: Input validation, authentication, authorization
3. **Data Layer**: Encryption at rest, secure database connections
4. **Infrastructure Layer**: Container security, network policies

### Security Principles

- **Zero Trust**: Every request is authenticated and authorized
- **Least Privilege**: Users and services have minimal required permissions
- **Defense in Depth**: Multiple security controls at each layer
- **Fail Secure**: System fails to secure state by default
- **Security by Design**: Security integrated from the beginning

## Authentication & Authorization

### JWT Implementation

#### Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@example.com",
    "user_type": "client",
    "permissions": ["read:profile", "write:bookings"],
    "iat": 1642248600,
    "exp": 1642252200,
    "jti": "unique_token_id"
  }
}
```

#### Token Security
- **Access Token**: Short-lived (30 minutes) for API access
- **Refresh Token**: Long-lived (7 days) for token renewal
- **Token Rotation**: Refresh tokens are rotated on each use
- **Token Blacklisting**: Revoked tokens are stored in Redis

#### Implementation
```python
from shared.utils import SecurityUtils

class JWTManager:
    @staticmethod
    def create_access_token(user_id: int, email: str, user_type: str) -> str:
        """Create JWT access token."""
        payload = {
            "sub": user_id,
            "email": email,
            "user_type": user_type,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return SecurityUtils.encode_jwt(payload)
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create JWT refresh token."""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=7),
            "jti": SecurityUtils.generate_secure_token()
        }
        return SecurityUtils.encode_jwt(payload)
```

### OAuth 2.0 Integration

#### Supported Providers
- **Google OAuth 2.0**: For Google account login
- **Facebook OAuth 2.0**: For Facebook account login
- **Apple Sign-In**: For Apple account login

#### Implementation
```python
from google.auth.transport import requests
from google.oauth2 import id_token

class OAuthService:
    @staticmethod
    async def verify_google_token(token: str) -> dict:
        """Verify Google OAuth token."""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            return {
                "email": idinfo["email"],
                "name": idinfo["name"],
                "picture": idinfo.get("picture"),
                "verified": idinfo["email_verified"]
            }
        except ValueError:
            raise InvalidTokenError("Invalid Google token")
```

### Multi-Factor Authentication (MFA)

#### TOTP Implementation
```python
import pyotp
from shared.utils import SecurityUtils

class MFAService:
    @staticmethod
    def generate_totp_secret() -> str:
        """Generate TOTP secret for user."""
        return pyotp.random_base32()
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def generate_qr_code(secret: str, email: str) -> str:
        """Generate QR code for TOTP setup."""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            email, 
            issuer_name="Kerya App"
        )
        return SecurityUtils.generate_qr_code(provisioning_uri)
```

## Data Protection

### Encryption

#### AES-256 Encryption
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class EncryptionService:
    def __init__(self, master_key: str):
        self.master_key = master_key.encode()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using AES-256."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(salt + encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        data = base64.urlsafe_b64decode(encrypted_data.encode())
        salt = data[:16]
        encrypted = data[16:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        f = Fernet(key)
        return f.decrypt(encrypted).decode()
```

#### Database Encryption
```python
# PostgreSQL encryption at rest
# Enable transparent data encryption (TDE)
# Configure encrypted connections

# Example connection string with SSL
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
```

### Data Masking

#### PII Protection
```python
from shared.utils import SecurityUtils

class DataMaskingService:
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address for display."""
        if "@" not in email:
            return email
        username, domain = email.split("@")
        masked_username = username[:2] + "*" * (len(username) - 2)
        return f"{masked_username}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number for display."""
        if len(phone) < 4:
            return phone
        return phone[:2] + "*" * (len(phone) - 4) + phone[-2:]
    
    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """Mask credit card number."""
        if len(card_number) < 4:
            return card_number
        return "*" * (len(card_number) - 4) + card_number[-4:]
```

## Input Validation & Sanitization

### Request Validation

#### Pydantic Models
```python
from pydantic import BaseModel, validator, EmailStr
import re

class UserCreateRequest(BaseModel):
    email: EmailStr
    phone: str
    password: str
    first_name: str
    last_name: str
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        """Validate name format."""
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
```

#### SQL Injection Prevention
```python
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class SecureDatabaseService:
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
        """Get user by email using parameterized query."""
        try:
            # Use parameterized query to prevent SQL injection
            stmt = text("SELECT * FROM users WHERE email = :email")
            result = await db.execute(stmt, {"email": email})
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise DatabaseError("Database operation failed")
```

### XSS Prevention

#### Input Sanitization
```python
import bleach
from html import escape

class XSSProtectionService:
    @staticmethod
    def sanitize_html(input_text: str) -> str:
        """Sanitize HTML input to prevent XSS."""
        # Allow only safe HTML tags and attributes
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
        allowed_attributes = {}
        
        return bleach.clean(
            input_text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def escape_html(input_text: str) -> str:
        """Escape HTML characters."""
        return escape(input_text)
```

## Rate Limiting & DDoS Protection

### Rate Limiting Implementation

#### Global Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Global rate limit
@app.middleware("http")
async def global_rate_limit(request: Request, call_next):
    """Apply global rate limiting."""
    client_ip = get_remote_address(request)
    
    # Check global rate limit
    if await limiter.is_allowed(client_ip, "global", 100, 60):
        response = await call_next(request)
        return response
    else:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
```

#### Per-Endpoint Rate Limiting
```python
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest):
    """Login endpoint with rate limiting."""
    # Login logic here
    pass

@router.post("/register")
@limiter.limit("3/hour")
async def register(request: Request, user_data: UserCreateRequest):
    """Registration endpoint with rate limiting."""
    # Registration logic here
    pass

@router.post("/verify-email")
@limiter.limit("10/hour")
async def verify_email(request: Request, verification_data: EmailVerificationRequest):
    """Email verification with rate limiting."""
    # Verification logic here
    pass
```

### DDoS Protection

#### Implementation
```python
from shared.utils import SecurityUtils

class DDoSProtectionService:
    def __init__(self):
        self.request_counts = {}
        self.blocked_ips = set()
    
    async def check_ddos(self, client_ip: str) -> bool:
        """Check for DDoS attack patterns."""
        current_time = time.time()
        
        # Clean old entries
        self.request_counts = {
            ip: count for ip, count in self.request_counts.items()
            if current_time - count['timestamp'] < 60
        }
        
        # Check request count
        if client_ip in self.request_counts:
            count = self.request_counts[client_ip]['count']
            if count > 1000:  # More than 1000 requests per minute
                self.blocked_ips.add(client_ip)
                return False
            self.request_counts[client_ip]['count'] += 1
        else:
            self.request_counts[client_ip] = {
                'count': 1,
                'timestamp': current_time
            }
        
        return client_ip not in self.blocked_ips
```

## Security Headers

### HTTP Security Headers
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.kerya.com", "https://admin.kerya.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.kerya.com", "*.kerya.com"]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
```

## Audit Logging

### Security Event Logging
```python
import structlog
from datetime import datetime
from typing import Dict, Any

class SecurityAuditLogger:
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def log_login_attempt(self, email: str, ip_address: str, success: bool):
        """Log login attempt."""
        self.logger.info(
            "Login attempt",
            email=email,
            ip_address=ip_address,
            success=success,
            timestamp=datetime.utcnow().isoformat(),
            event_type="login_attempt"
        )
    
    def log_password_change(self, user_id: int, ip_address: str):
        """Log password change."""
        self.logger.info(
            "Password changed",
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow().isoformat(),
            event_type="password_change"
        )
    
    def log_sensitive_data_access(self, user_id: int, data_type: str, ip_address: str):
        """Log sensitive data access."""
        self.logger.info(
            "Sensitive data accessed",
            user_id=user_id,
            data_type=data_type,
            ip_address=ip_address,
            timestamp=datetime.utcnow().isoformat(),
            event_type="sensitive_data_access"
        )
    
    def log_security_violation(self, violation_type: str, details: Dict[str, Any]):
        """Log security violation."""
        self.logger.warning(
            "Security violation detected",
            violation_type=violation_type,
            details=details,
            timestamp=datetime.utcnow().isoformat(),
            event_type="security_violation"
        )
```

## Vulnerability Management

### Security Scanning

#### Dependency Scanning
```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'kerya/user-service:latest'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

#### Code Security Analysis
```python
# bandit configuration
# .bandit
exclude_dirs: ['tests', 'venv']
skips: ['B101', 'B601']

# Run bandit
# bandit -r . -f json -o bandit-report.json
```

### Security Testing

#### Penetration Testing
```python
# Security test examples
import pytest
from httpx import AsyncClient

class TestSecurity:
    async def test_sql_injection_prevention(self, client: AsyncClient):
        """Test SQL injection prevention."""
        response = await client.get(
            "/users/search",
            params={"q": "'; DROP TABLE users; --"}
        )
        assert response.status_code == 400
    
    async def test_xss_prevention(self, client: AsyncClient):
        """Test XSS prevention."""
        response = await client.post(
            "/users/profile",
            json={"bio": "<script>alert('xss')</script>"}
        )
        assert response.status_code == 422
    
    async def test_csrf_protection(self, client: AsyncClient):
        """Test CSRF protection."""
        response = await client.post(
            "/users/change-password",
            headers={"X-CSRF-Token": "invalid-token"}
        )
        assert response.status_code == 403
```

## Incident Response

### Security Incident Response Plan

#### 1. Detection
- Automated monitoring and alerting
- Manual reporting through security@kerya.com
- Third-party security monitoring

#### 2. Assessment
- Immediate impact assessment
- Scope determination
- Risk level classification

#### 3. Containment
- Isolate affected systems
- Block malicious IPs
- Disable compromised accounts

#### 4. Eradication
- Remove malware/backdoors
- Patch vulnerabilities
- Update security controls

#### 5. Recovery
- Restore systems from clean backups
- Verify system integrity
- Monitor for recurrence

#### 6. Lessons Learned
- Document incident details
- Update security procedures
- Conduct post-incident review

### Incident Response Team

- **Security Lead**: Overall incident coordination
- **DevOps Engineer**: System recovery and patching
- **Database Administrator**: Data integrity and recovery
- **Legal Counsel**: Compliance and notification requirements
- **Communications**: Customer and stakeholder communication

## Compliance

### GDPR Compliance

#### Data Protection Measures
```python
class GDPRComplianceService:
    @staticmethod
    async def process_data_deletion_request(user_id: int, db: AsyncSession):
        """Process GDPR data deletion request."""
        # Anonymize personal data
        await user_service.anonymize_user_data(user_id, db)
        
        # Delete user account
        await user_service.delete_user_account(user_id, db)
        
        # Log deletion request
        audit_logger.log_data_deletion(user_id, "GDPR request")
    
    @staticmethod
    async def process_data_export_request(user_id: int, db: AsyncSession):
        """Process GDPR data export request."""
        user_data = await user_service.get_user_data_for_export(user_id, db)
        return user_data
```

#### Privacy Policy Implementation
```python
class PrivacyService:
    @staticmethod
    async def get_privacy_consent(user_id: int) -> Dict[str, bool]:
        """Get user privacy consent status."""
        return await user_service.get_consent_status(user_id)
    
    @staticmethod
    async def update_privacy_consent(
        user_id: int, 
        consent_type: str, 
        granted: bool
    ):
        """Update user privacy consent."""
        await user_service.update_consent(user_id, consent_type, granted)
        audit_logger.log_consent_update(user_id, consent_type, granted)
```

### PCI DSS Compliance

#### Payment Data Protection
```python
class PaymentSecurityService:
    @staticmethod
    def tokenize_payment_data(card_number: str) -> str:
        """Tokenize payment data for PCI compliance."""
        # Use Stripe or similar service for tokenization
        return stripe.Token.create(card={'number': card_number})
    
    @staticmethod
    def validate_pci_compliance(payment_data: Dict) -> bool:
        """Validate PCI DSS compliance."""
        # Implement PCI DSS validation checks
        return True
```

## Security Monitoring

### Real-time Monitoring

#### Security Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Security metrics
failed_login_attempts = Counter(
    'failed_login_attempts_total',
    'Total failed login attempts',
    ['ip_address', 'user_agent']
)

security_violations = Counter(
    'security_violations_total',
    'Total security violations',
    ['violation_type', 'severity']
)

active_sessions = Gauge(
    'active_sessions_total',
    'Total active user sessions'
)

authentication_duration = Histogram(
    'authentication_duration_seconds',
    'Time spent on authentication',
    ['method']
)
```

#### Alerting Rules
```yaml
# prometheus/rules/security.yml
groups:
  - name: security.rules
    rules:
      - alert: HighFailedLoginAttempts
        expr: rate(failed_login_attempts_total[5m]) > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: High number of failed login attempts detected
      
      - alert: SecurityViolationDetected
        expr: rate(security_violations_total[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: Security violation detected
```

## Security Training

### Developer Security Guidelines

1. **Secure Coding Practices**
   - Always validate and sanitize input
   - Use parameterized queries
   - Implement proper error handling
   - Follow the principle of least privilege

2. **Code Review Security Checklist**
   - [ ] Input validation implemented
   - [ ] SQL injection prevention
   - [ ] XSS protection
   - [ ] Authentication/authorization checks
   - [ ] Sensitive data handling
   - [ ] Error handling without information disclosure

3. **Security Testing Requirements**
   - Unit tests for security functions
   - Integration tests for security flows
   - Penetration testing for new features
   - Dependency vulnerability scanning

### Security Awareness Training

- **Quarterly security training** for all developers
- **Security incident response drills**
- **Phishing awareness training**
- **Secure development lifecycle training**

## Security Tools

### Recommended Security Tools

1. **Static Analysis**
   - Bandit (Python security linter)
   - Semgrep (Security-focused static analysis)
   - SonarQube (Code quality and security)

2. **Dynamic Analysis**
   - OWASP ZAP (Web application security scanner)
   - Burp Suite (Web application security testing)
   - Nikto (Web server scanner)

3. **Dependency Scanning**
   - Trivy (Container and dependency vulnerability scanner)
   - Snyk (Dependency vulnerability management)
   - Safety (Python dependency security checker)

4. **Monitoring**
   - Prometheus (Metrics collection)
   - Grafana (Metrics visualization)
   - ELK Stack (Log analysis)

This security documentation provides comprehensive guidance for maintaining the security of the Kerya App. Regular updates and reviews are essential to address emerging threats and maintain compliance with security standards. 