# Kerya App Back-End

A scalable, secure microservices-based back-end for a property rental platform similar to Airbnb, with features for hotels, events, and a client-driven posting system.

## 🏗️ Architecture Overview

The Kerya App back-end is built using a microservices architecture with the following components:

- **API Gateway**: FastAPI-based gateway with authentication, rate limiting, and load balancing
- **User Service**: Authentication, profile management, and points system
- **Property Service**: CRUD operations, search/filter, and image management
- **Booking Service**: Reservation logic and payment processing
- **Notification Service**: Async notifications via email, SMS, and push
- **Review Service**: Rating and comment management
- **Post Service**: Client post creation and host matching

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (primary), Redis (cache/sessions), Elasticsearch (search)
- **Message Queue**: RabbitMQ for async tasks
- **File Storage**: AWS S3 for property images
- **External APIs**: Google Maps, SendGrid, Twilio
- **DevOps**: Docker, Kubernetes, Nginx
- **Monitoring**: Prometheus, Grafana, ELK Stack, Jaeger
- **Security**: JWT/OAuth 2.0, RBAC, TLS 1.3, AES-256 encryption

## 📁 Project Structure

```
server/
├── api_gateway/           # API Gateway service
├── user_service/          # User management and authentication
├── property_service/      # Property CRUD and search
├── booking_service/       # Booking and reservation logic
├── notification_service/  # Async notifications
├── review_service/        # Review and rating system
├── post_service/          # Client post management
├── shared/                # Shared utilities and models
├── docker-compose.yml     # Local development setup
├── kubernetes/            # K8s deployment manifests
├── monitoring/            # Prometheus, Grafana configs
└── scripts/               # Setup and deployment scripts
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Elasticsearch 7+

### Local Development Setup

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd server
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**:
   ```bash
   docker-compose exec user_service alembic upgrade head
   docker-compose exec property_service alembic upgrade head
   docker-compose exec booking_service alembic upgrade head
   ```

4. **Access the API**:
   - API Gateway: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Grafana: http://localhost:3000
   - Kibana: http://localhost:5601

### Production Deployment

1. **Deploy to Kubernetes**:
   ```bash
   kubectl apply -f kubernetes/
   ```

2. **Configure ingress and SSL**:
   ```bash
   kubectl apply -f kubernetes/ingress/
   ```

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - User logout

### User Endpoints

- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `POST /api/v1/users/verify` - Verify user account
- `GET /api/v1/users/points` - Get user points

### Property Endpoints

- `GET /api/v1/properties` - List properties with search/filter
- `POST /api/v1/properties` - Create new property
- `GET /api/v1/properties/{id}` - Get property details
- `PUT /api/v1/properties/{id}` - Update property
- `DELETE /api/v1/properties/{id}` - Delete property

### Booking Endpoints

- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings` - List user bookings
- `PUT /api/v1/bookings/{id}/confirm` - Confirm booking
- `PUT /api/v1/bookings/{id}/cancel` - Cancel booking

### Post Endpoints

- `GET /api/v1/posts` - List client posts
- `POST /api/v1/posts` - Create client post
- `GET /api/v1/posts/{id}` - Get post details
- `POST /api/v1/posts/{id}/contact` - Contact post creator

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ELASTICSEARCH_URL`: Elasticsearch connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `AWS_ACCESS_KEY_ID`: AWS S3 access key
- `AWS_SECRET_ACCESS_KEY`: AWS S3 secret key
- `JWT_SECRET_KEY`: JWT signing secret
- `SENDGRID_API_KEY`: SendGrid API key
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `GOOGLE_MAPS_API_KEY`: Google Maps API key

### Database Configuration

The application uses PostgreSQL with the following main tables:

- `users`: User accounts and profiles
- `properties`: Property listings
- `bookings`: Reservation records
- `reviews`: Property reviews and ratings
- `posts`: Client post requests
- `messages`: User messaging
- `notifications`: System notifications

## 🧪 Testing

### Run Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Load testing
locust -f tests/load/locustfile.py
```

### Test Coverage

```bash
pytest --cov=app tests/
```

## 📊 Monitoring

### Metrics

- Prometheus metrics available at `/metrics` endpoints
- Grafana dashboards for application and infrastructure metrics
- Custom business metrics (bookings, revenue, user growth)

### Logging

- Centralized logging with ELK Stack
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Tracing

- Distributed tracing with Jaeger
- Request correlation across microservices
- Performance bottleneck identification

## 🔒 Security

### Authentication & Authorization

- JWT-based authentication with refresh tokens
- OAuth 2.0 integration for Google login
- Role-based access control (RBAC)
- API key management for external integrations

### Data Protection

- AES-256 encryption for sensitive data
- TLS 1.3 for all communications
- Input validation and sanitization
- Rate limiting and DDoS protection

## 🚀 Deployment

### Docker

Each service has its own Dockerfile optimized for production:

```bash
# Build images
docker build -t kerya/user-service ./user_service/
docker build -t kerya/property-service ./property_service/
# ... other services

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

Production deployment with Kubernetes:

```bash
# Deploy to cluster
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -n kerya-app

# View logs
kubectl logs -f deployment/user-service -n kerya-app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation at `/docs`
- Review the API documentation at `/docs`

## 🔄 Next Steps

1. **Review and customize** the generated code for your specific requirements
2. **Configure external services** (AWS S3, SendGrid, Twilio, Google Maps)
3. **Set up monitoring and alerting** for production
4. **Implement additional features** based on business requirements
5. **Add comprehensive testing** for all endpoints
6. **Optimize performance** with caching and database indexing 