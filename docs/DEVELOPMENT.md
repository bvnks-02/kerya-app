# Kerya App Development Guide

## Overview

This guide provides comprehensive information for developers contributing to the Kerya App back-end. It covers the development environment setup, coding standards, testing procedures, and contribution guidelines.

## Development Environment Setup

### Prerequisites

- **Python**: 3.9 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **Git**: Latest version
- **IDE**: VS Code, PyCharm, or similar
- **Postman** or **Insomnia**: For API testing

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/kerya-app.git
   cd kerya-app/server
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your local configuration
   ```

5. **Start development services**:
   ```bash
   docker-compose up -d postgres redis elasticsearch rabbitmq
   ```

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

### IDE Configuration

#### VS Code Settings

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

#### PyCharm Configuration

1. **Set project interpreter** to the virtual environment
2. **Configure code style** to use Black formatter
3. **Enable auto-imports** and organize imports on save
4. **Set up run configurations** for individual services

## Project Structure

```
server/
├── api_gateway/           # API Gateway service
├── user_service/          # User management service
├── property_service/      # Property management service
├── booking_service/       # Booking management service
├── notification_service/  # Notification service
├── review_service/        # Review management service
├── post_service/          # Post management service
├── shared/               # Shared utilities and models
├── kubernetes/           # Kubernetes manifests
├── scripts/              # Utility scripts
├── docs/                 # Documentation
├── tests/                # Test files
├── docker-compose.yml    # Local development setup
├── requirements.txt      # Python dependencies
└── README.md            # Project overview
```

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 88 characters (Black default)
- **Import order**: Standard library → Third-party → Local imports
- **Docstrings**: Google style
- **Type hints**: Required for all function parameters and return values

### Code Formatting

We use **Black** for code formatting and **isort** for import sorting:

```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8 .

# Type checking
mypy .
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Development Workflow

### Feature Development

1. **Create feature branch**:
   ```bash
   git checkout -b feature/user-profile-enhancement
   ```

2. **Make changes** following coding standards

3. **Write tests** for new functionality

4. **Run tests locally**:
   ```bash
   pytest tests/
   ```

5. **Format and lint code**:
   ```bash
   black .
   isort .
   flake8 .
   mypy .
   ```

6. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: enhance user profile with additional fields"
   ```

7. **Push and create pull request**

### Service Development

#### Adding a New Service

1. **Create service directory**:
   ```bash
   mkdir new_service
   cd new_service
   ```

2. **Create service structure**:
   ```
   new_service/
   ├── __init__.py
   ├── main.py
   ├── config.py
   ├── database.py
   ├── models.py
   ├── routes/
   │   ├── __init__.py
   │   └── api.py
   ├── services/
   │   ├── __init__.py
   │   └── business_logic.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_api.py
   │   └── test_services.py
   ├── Dockerfile
   └── requirements.txt
   ```

3. **Add to docker-compose.yml**:
   ```yaml
   new_service:
     build: ./new_service
     ports:
       - "8007:8000"
     environment:
       - DATABASE_URL=postgresql://user:pass@postgres:5432/kerya_db
     depends_on:
       - postgres
       - redis
   ```

4. **Add to Kubernetes manifests**:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: kerya-new-service
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: kerya-new-service
     template:
       metadata:
         labels:
           app: kerya-new-service
       spec:
         containers:
         - name: new-service
           image: kerya/new-service:latest
           ports:
           - containerPort: 8000
   ```

#### Adding New Endpoints

1. **Create route file** in `routes/` directory
2. **Define Pydantic models** in `models.py`
3. **Implement business logic** in `services/` directory
4. **Write tests** for the new endpoints
5. **Update API documentation**

Example endpoint:
```python
from fastapi import APIRouter, Depends, HTTPException
from shared.utils import ResponseUtils, LoggingUtils
from .models import CreateItemRequest, ItemResponse
from .services import ItemService

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemResponse)
async def create_item(
    request: CreateItemRequest,
    service: ItemService = Depends(),
    logger = Depends(LoggingUtils.get_logger)
):
    """Create a new item."""
    try:
        item = await service.create_item(request)
        logger.info("Item created successfully", item_id=item.id)
        return ResponseUtils.success_response(
            message="Item created successfully",
            data=item
        )
    except Exception as e:
        logger.error("Failed to create item", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/          # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_external_apis.py
├── e2e/                  # End-to-end tests
│   ├── test_booking_flow.py
│   └── test_user_journey.py
├── fixtures/             # Test fixtures
│   ├── users.py
│   ├── properties.py
│   └── bookings.py
└── conftest.py          # Pytest configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run tests in parallel
pytest -n auto

# Run integration tests only
pytest tests/integration/

# Run tests with specific marker
pytest -m "slow"
```

### Test Examples

#### Unit Test
```python
import pytest
from unittest.mock import Mock, patch
from user_service.services import UserService
from user_service.models import UserCreateRequest

class TestUserService:
    @pytest.fixture
    def user_service(self):
        return UserService()

    @pytest.fixture
    def user_data(self):
        return UserCreateRequest(
            email="test@example.com",
            phone="+1234567890",
            password="SecurePass123!",
            first_name="John",
            last_name="Doe"
        )

    async def test_create_user_success(self, user_service, user_data):
        """Test successful user creation."""
        with patch('user_service.services.SecurityUtils.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            user = await user_service.create_user(user_data)
            
            assert user.email == user_data.email
            assert user.phone == user_data.phone
            assert user.first_name == user_data.first_name
            assert user.last_name == user_data.last_name
```

#### Integration Test
```python
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from user_service.main import app

class TestUserAPI:
    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    async def test_register_user(self, client):
        """Test user registration endpoint."""
        response = await client.post("/auth/register", json={
            "email": "test@example.com",
            "phone": "+1234567890",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
```

### Test Fixtures

Create reusable test data in `tests/fixtures/`:

```python
# tests/fixtures/users.py
import pytest
from user_service.models import UserCreateRequest

@pytest.fixture
def sample_user_data():
    return UserCreateRequest(
        email="test@example.com",
        phone="+1234567890",
        password="SecurePass123!",
        first_name="John",
        last_name="Doe",
        user_type="client"
    )

@pytest.fixture
def sample_host_data():
    return UserCreateRequest(
        email="host@example.com",
        phone="+1234567891",
        password="SecurePass123!",
        first_name="Jane",
        last_name="Smith",
        user_type="host"
    )
```

## Database Development

### Migration Workflow

1. **Create migration**:
   ```bash
   alembic revision --autogenerate -m "Add user preferences table"
   ```

2. **Review migration file** in `alembic/versions/`

3. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

4. **Rollback if needed**:
   ```bash
   alembic downgrade -1
   ```

### Database Seeding

Create seed data scripts:

```python
# scripts/seed_data.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from user_service.models import User
from shared.utils import SecurityUtils

async def seed_users():
    """Seed initial users for development."""
    async for db in get_db():
        # Create admin user
        admin_user = User(
            email="admin@kerya.com",
            phone="+1234567890",
            password_hash=SecurityUtils.hash_password("AdminPass123!"),
            first_name="Admin",
            last_name="User",
            user_type="admin",
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed_users())
```

## API Development

### Adding New Endpoints

1. **Define request/response models**:
   ```python
   from pydantic import BaseModel, EmailStr
   from typing import Optional
   from datetime import datetime

   class UpdateProfileRequest(BaseModel):
       first_name: Optional[str] = None
       last_name: Optional[str] = None
       phone: Optional[str] = None
       profile_image: Optional[str] = None

   class ProfileResponse(BaseModel):
       id: int
       email: str
       first_name: str
       last_name: str
       phone: str
       profile_image: Optional[str]
       rating: float
       points: int
       created_at: datetime
       updated_at: datetime
   ```

2. **Implement endpoint**:
   ```python
   @router.put("/profile", response_model=ProfileResponse)
   async def update_profile(
       request: UpdateProfileRequest,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       """Update user profile."""
       updated_user = await user_service.update_profile(
           db, current_user.id, request
       )
       return ResponseUtils.success_response(
           message="Profile updated successfully",
           data=updated_user
       )
   ```

3. **Add validation**:
   ```python
   from pydantic import validator

   class UpdateProfileRequest(BaseModel):
       first_name: Optional[str] = None
       last_name: Optional[str] = None
       phone: Optional[str] = None
       profile_image: Optional[str] = None

       @validator('phone')
       def validate_phone(cls, v):
           if v and not ValidationUtils.is_valid_phone(v):
               raise ValueError('Invalid phone number format')
           return v
   ```

### Error Handling

Implement consistent error handling:

```python
from fastapi import HTTPException
from shared.utils import LoggingUtils

class UserServiceError(Exception):
    """Base exception for user service errors."""
    pass

class UserNotFoundError(UserServiceError):
    """Raised when user is not found."""
    pass

class InvalidCredentialsError(UserServiceError):
    """Raised when credentials are invalid."""
    pass

async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    """Get user by ID with proper error handling."""
    try:
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user
    except UserNotFoundError:
        raise
    except Exception as e:
        LoggingUtils.get_logger().error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Monitoring and Debugging

### Logging

Use structured logging throughout the application:

```python
import structlog
from shared.utils import LoggingUtils

logger = LoggingUtils.get_logger(__name__)

async def create_booking(booking_data: CreateBookingRequest):
    """Create a new booking with detailed logging."""
    logger.info(
        "Creating booking",
        user_id=booking_data.user_id,
        property_id=booking_data.property_id,
        check_in=booking_data.check_in_date,
        check_out=booking_data.check_out_date
    )
    
    try:
        booking = await booking_service.create(booking_data)
        logger.info(
            "Booking created successfully",
            booking_id=booking.id,
            total_price=booking.total_price
        )
        return booking
    except Exception as e:
        logger.error(
            "Failed to create booking",
            error=str(e),
            user_id=booking_data.user_id,
            property_id=booking_data.property_id
        )
        raise
```

### Metrics

Record custom metrics for monitoring:

```python
from shared.utils import MetricsUtils

async def process_payment(payment_data: PaymentRequest):
    """Process payment with metrics recording."""
    start_time = time.time()
    
    try:
        result = await payment_service.process(payment_data)
        MetricsUtils.record_payment_success(
            amount=payment_data.amount,
            payment_method=payment_data.method
        )
        return result
    except Exception as e:
        MetricsUtils.record_payment_failure(
            amount=payment_data.amount,
            payment_method=payment_data.method,
            error=str(e)
        )
        raise
    finally:
        processing_time = time.time() - start_time
        MetricsUtils.record_payment_processing_time(processing_time)
```

### Debugging

#### Local Debugging

1. **Use debugger**:
   ```python
   import pdb; pdb.set_trace()  # Python debugger
   ```

2. **Add debug logging**:
   ```python
   logger.debug(f"Variable value: {variable}")
   ```

3. **Use FastAPI debug mode**:
   ```bash
   uvicorn main:app --reload --log-level debug
   ```

#### Remote Debugging

1. **Enable remote debugging** in Docker:
   ```dockerfile
   EXPOSE 5678
   CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Connect from IDE** to `localhost:5678`

## Performance Optimization

### Database Optimization

1. **Use indexes** for frequently queried columns:
   ```python
   class User(Base):
       __tablename__ = "users"
       
       id = Column(Integer, primary_key=True, index=True)
       email = Column(String, unique=True, index=True)
       phone = Column(String, unique=True, index=True)
       user_type = Column(Enum(UserType), index=True)
   ```

2. **Optimize queries**:
   ```python
   # Bad: N+1 query problem
   users = await db.execute(select(User))
   for user in users.scalars():
       bookings = await db.execute(select(Booking).where(Booking.user_id == user.id))
   
   # Good: Use joins
   stmt = select(User).options(selectinload(User.bookings))
   users = await db.execute(stmt)
   ```

3. **Use connection pooling**:
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True
   )
   ```

### Caching

Implement Redis caching for expensive operations:

```python
from shared.utils import CacheUtils

async def get_property_details(property_id: int, db: AsyncSession):
    """Get property details with caching."""
    cache_key = f"property:{property_id}"
    
    # Try cache first
    cached_data = await CacheUtils.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch from database
    property_data = await property_service.get_by_id(property_id, db)
    
    # Cache for 5 minutes
    await CacheUtils.set(cache_key, property_data, ttl=300)
    
    return property_data
```

## Security Best Practices

### Input Validation

1. **Use Pydantic models** for all inputs:
   ```python
   from pydantic import BaseModel, validator, EmailStr
   import re

   class UserCreateRequest(BaseModel):
       email: EmailStr
       password: str
       phone: str
       
       @validator('password')
       def validate_password(cls, v):
           if len(v) < 8:
               raise ValueError('Password must be at least 8 characters')
           if not re.search(r'[A-Z]', v):
               raise ValueError('Password must contain uppercase letter')
           if not re.search(r'[a-z]', v):
               raise ValueError('Password must contain lowercase letter')
           if not re.search(r'\d', v):
               raise ValueError('Password must contain number')
           return v
   ```

2. **Sanitize inputs**:
   ```python
   from shared.utils import SecurityUtils
   
   def sanitize_input(input_string: str) -> str:
       """Sanitize user input to prevent XSS."""
       return SecurityUtils.sanitize_html(input_string)
   ```

### Authentication

1. **Implement proper JWT handling**:
   ```python
   from shared.utils import SecurityUtils
   
   async def authenticate_user(email: str, password: str, db: AsyncSession):
       """Authenticate user with proper security."""
       user = await user_service.get_by_email(email, db)
       if not user:
           raise InvalidCredentialsError("Invalid email or password")
       
       if not SecurityUtils.verify_password(password, user.password_hash):
           # Record failed login attempt
           await user_service.record_failed_login(user.id, db)
           raise InvalidCredentialsError("Invalid email or password")
       
       return user
   ```

2. **Rate limiting**:
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @router.post("/login")
   @limiter.limit("5/minute")
   async def login(request: Request, login_data: LoginRequest):
       # Login logic here
       pass
   ```

## Documentation

### Code Documentation

1. **Docstrings** for all functions:
   ```python
   async def create_booking(
       booking_data: CreateBookingRequest,
       current_user: User,
       db: AsyncSession
   ) -> Booking:
       """
       Create a new booking for a property.
       
       Args:
           booking_data: Booking request data
           current_user: Authenticated user
           db: Database session
           
       Returns:
           Created booking object
           
       Raises:
           PropertyNotAvailableError: If property is not available
           InsufficientPointsError: If user doesn't have enough points
           ValidationError: If booking data is invalid
       """
   ```

2. **Type hints** for all functions:
   ```python
   from typing import List, Optional, Dict, Any
   
   async def get_user_bookings(
       user_id: int,
       status: Optional[str] = None,
       limit: int = 20,
       offset: int = 0
   ) -> Dict[str, Any]:
       """Get user bookings with pagination."""
   ```

### API Documentation

1. **Update OpenAPI schema**:
   ```python
   from fastapi import FastAPI
   
   app = FastAPI(
       title="Kerya App API",
       description="Property rental platform API",
       version="1.0.0",
       docs_url="/docs",
       redoc_url="/redoc"
   )
   ```

2. **Add response examples**:
   ```python
   from fastapi import Body
   
   @router.post("/register", response_model=AuthResponse)
   async def register(
       user_data: UserCreateRequest = Body(
           ...,
           example={
               "email": "user@example.com",
               "phone": "+1234567890",
               "password": "SecurePass123!",
               "first_name": "John",
               "last_name": "Doe"
           }
       )
   ):
   ```

## Contribution Guidelines

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** following coding standards
4. **Write tests** for new functionality
5. **Update documentation** if needed
6. **Run all tests**: `pytest`
7. **Format code**: `black . && isort .`
8. **Commit changes**: `git commit -m "feat: add amazing feature"`
9. **Push to branch**: `git push origin feature/amazing-feature`
10. **Create pull request**

### Commit Message Format

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:
```
feat(auth): add OAuth2 support for Google login
fix(booking): resolve timezone issue in booking dates
docs(api): update authentication endpoint documentation
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] No hardcoded secrets
- [ ] Environment variables are used correctly

This development guide provides comprehensive information for contributing to the Kerya App back-end. Follow these guidelines to ensure code quality and maintainability. 