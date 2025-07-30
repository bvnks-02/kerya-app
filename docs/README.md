# Kerya App Documentation

Welcome to the Kerya App documentation! This comprehensive guide covers all aspects of the property rental platform back-end.

## 📚 Documentation Overview

### 🏗️ Architecture & Design
- **[Architecture Guide](ARCHITECTURE.md)** - Complete system architecture, design decisions, and technical overview
- **[API Documentation](API_DOCUMENTATION.md)** - Comprehensive API reference with examples and error codes
- **[Security Documentation](SECURITY.md)** - Security measures, best practices, and compliance guidelines

### 🚀 Deployment & Operations
- **[Deployment Guide](DEPLOYMENT.md)** - Step-by-step deployment instructions for all environments
- **[Development Guide](DEVELOPMENT.md)** - Development environment setup and contribution guidelines

### 📋 Quick Start Guides

#### For Developers
1. **Setup Development Environment**
   ```bash
   git clone https://github.com/your-org/kerya-app.git
   cd kerya-app/server
   chmod +x scripts/setup.sh
   ./scripts/setup.sh development
   ```

2. **Access Services**
   - API Gateway: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3000
   - Kibana: http://localhost:5601

#### For DevOps Engineers
1. **Production Deployment**
   ```bash
   # Using Kubernetes
   kubectl apply -f kubernetes/namespace.yaml
   kubectl apply -f kubernetes/configmap.yaml
   kubectl apply -f kubernetes/secret.yaml
   kubectl apply -f kubernetes/
   ```

2. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🏛️ System Architecture

The Kerya App follows a microservices architecture with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                        API Gateway                              │
│  • Request Routing & Load Balancing                            │
│  • Authentication & Authorization                              │
│  • Rate Limiting & DDoS Protection                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Microservices Layer                          │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ User Service│  │Property Svc │  │Booking Svc  │            │
│  │ • Auth      │  │ • CRUD      │  │ • Reserv.   │            │
│  │ • Profile   │  │ • Search    │  │ • Calendar  │            │
│  │ • Points    │  │ • Images    │  │ • Payments  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │Notification │  │Review Svc   │  │Post Service │            │
│  │ • Email     │  │ • Ratings   │  │ • Posts     │            │
│  │ • SMS       │  │ • Comments  │  │ • Matching  │            │
│  │ • Push      │  │ • Analytics │  │ • Points    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Infrastructure Layer                         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ PostgreSQL  │  │   Redis     │  │Elasticsearch│            │
│  │ • Primary   │  │ • Cache     │  │ • Search    │            │
│  │ • ACID      │  │ • Sessions  │  │ • Analytics │            │
│  │ • Relations │  │ • Queues    │  │ • Logs      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  RabbitMQ   │  │  Prometheus │  │   Jaeger    │            │
│  │ • Messages  │  │ • Metrics   │  │ • Tracing   │            │
│  │ • Events    │  │ • Alerts    │  │ • Debug     │            │
│  │ • Queues    │  │ • Monitoring│  │ • Profiling │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Technology Stack

### Core Technologies
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Search**: Elasticsearch 8
- **Message Queue**: RabbitMQ 3.12
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes

### External Services
- **File Storage**: AWS S3
- **Email**: SendGrid
- **SMS**: Twilio
- **Maps**: Google Maps API
- **Payments**: Stripe
- **Monitoring**: Prometheus, Grafana, ELK Stack

### Security
- **Authentication**: JWT/OAuth 2.0
- **Encryption**: AES-256
- **Rate Limiting**: SlowAPI
- **CORS**: Configured for production domains

## 📊 Key Features

### User Management
- ✅ User registration and authentication
- ✅ Email and phone verification
- ✅ Multi-factor authentication (TOTP)
- ✅ Role-based access control (RBAC)
- ✅ Points system for rewards

### Property Management
- ✅ Property CRUD operations
- ✅ Image upload and management
- ✅ Advanced search and filtering
- ✅ Geolocation-based search
- ✅ Availability calendar

### Booking System
- ✅ Real-time availability checking
- ✅ Booking creation and management
- ✅ Payment processing
- ✅ Cancellation policies
- ✅ Refund handling

### Communication
- ✅ Email notifications
- ✅ SMS notifications
- ✅ Push notifications
- ✅ In-app messaging
- ✅ Notification preferences

### Reviews & Ratings
- ✅ Review creation and moderation
- ✅ Rating aggregation
- ✅ Sentiment analysis
- ✅ Review analytics

### Client Posts
- ✅ Post creation for property requests
- ✅ Host matching algorithm
- ✅ Points-based posting system
- ✅ Post moderation

## 🚀 Quick API Examples

### Authentication
```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "phone": "+1234567890",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Property Search
```bash
# Search properties
curl -X GET "http://localhost:8000/api/v1/properties?wilaya=Algiers&min_price=50&max_price=200" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Booking
```bash
# Create a booking
curl -X POST "http://localhost:8000/api/v1/bookings" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 1,
    "check_in_date": "2024-02-01",
    "check_out_date": "2024-02-05",
    "guests_count": 2
  }'
```

## 📈 Monitoring & Observability

### Metrics Dashboard
- **API Response Times**: Monitor endpoint performance
- **Error Rates**: Track application errors
- **User Activity**: Monitor user engagement
- **Business Metrics**: Track bookings, revenue, etc.

### Logging
- **Structured Logging**: JSON format logs
- **Centralized Logging**: ELK Stack integration
- **Log Correlation**: Request ID tracking
- **Security Logging**: Audit trail for security events

### Tracing
- **Distributed Tracing**: Jaeger integration
- **Performance Analysis**: Identify bottlenecks
- **Service Dependencies**: Map service interactions

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- OAuth 2.0 integration (Google, Facebook, Apple)
- Role-based access control (RBAC)
- Multi-factor authentication (TOTP)

### Data Protection
- AES-256 encryption for sensitive data
- TLS 1.3 for data in transit
- Database encryption at rest
- PII masking and protection

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security (HSTS)

### Rate Limiting & DDoS Protection
- Global rate limiting
- Per-endpoint rate limiting
- DDoS detection and mitigation
- IP blocking for malicious activity

## 🛠️ Development Workflow

### Code Quality
- **Linting**: Black, isort, flake8, mypy
- **Testing**: pytest with coverage
- **Security**: Bandit vulnerability scanning
- **Pre-commit**: Automated code quality checks

### CI/CD Pipeline
- **Automated Testing**: Unit, integration, and security tests
- **Code Quality**: Automated linting and formatting
- **Security Scanning**: Dependency and container scanning
- **Deployment**: Automated deployment to staging and production

### Git Workflow
- **Branch Strategy**: GitFlow with main, develop, and feature branches
- **Pull Requests**: Required code review and approval
- **Commit Messages**: Conventional commits format
- **Release Management**: Semantic versioning

## 📋 Environment Setup

### Development Environment
```bash
# Prerequisites
- Python 3.11+
- Docker Desktop
- Docker Compose
- Git

# Quick Setup
git clone https://github.com/your-org/kerya-app.git
cd kerya-app/server
./scripts/setup.sh development
```

### Production Environment
```bash
# Prerequisites
- Kubernetes cluster (v1.24+)
- kubectl
- Helm (optional)
- SSL certificates
- Domain name

# Deployment
kubectl apply -f kubernetes/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](../CONTRIBUTING.md) for details.

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

### Development Standards
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Follow security best practices

## 📞 Support

### Documentation Issues
- Create an issue in the repository
- Tag with `documentation` label

### Technical Support
- Check existing issues and discussions
- Create a new issue with detailed information
- Contact maintainers for urgent issues

### Security Issues
- Report security vulnerabilities privately to security@kerya.com
- Do not create public issues for security concerns

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🗺️ Roadmap

### Upcoming Features
- [ ] Real-time chat functionality
- [ ] Advanced analytics dashboard
- [ ] Mobile app API endpoints
- [ ] Multi-language support
- [ ] Advanced payment methods
- [ ] AI-powered recommendations

### Planned Improvements
- [ ] Performance optimization
- [ ] Enhanced security features
- [ ] Improved monitoring
- [ ] Better documentation
- [ ] More comprehensive testing

---

**Happy coding! 🚀**

For more detailed information, please refer to the specific documentation files listed above. 