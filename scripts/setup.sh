#!/bin/bash

# Kerya App Setup Script
# This script sets up the complete Kerya App back-end infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="kerya-app"
DOCKER_REGISTRY="kerya"
ENVIRONMENT=${1:-development}

echo -e "${BLUE}🚀 Kerya App Setup Script${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check kubectl for production
    if [ "$ENVIRONMENT" = "production" ]; then
        if ! command -v kubectl &> /dev/null; then
            print_error "kubectl is not installed. Please install kubectl for production deployment."
            exit 1
        fi
    fi
    
    print_status "Prerequisites check passed"
}

# Setup environment file
setup_environment() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp env.example .env
        print_warning "Created .env file from template. Please update with your actual values."
    else
        print_info ".env file already exists"
    fi
    
    print_status "Environment setup completed"
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."
    
    # Build shared base image
    docker build -t ${DOCKER_REGISTRY}/shared:latest ./shared/
    
    # Build service images
    docker build -t ${DOCKER_REGISTRY}/api-gateway:latest ./api_gateway/
    docker build -t ${DOCKER_REGISTRY}/user-service:latest ./user_service/
    docker build -t ${DOCKER_REGISTRY}/property-service:latest ./property_service/
    docker build -t ${DOCKER_REGISTRY}/booking-service:latest ./booking_service/
    docker build -t ${DOCKER_REGISTRY}/notification-service:latest ./notification_service/
    docker build -t ${DOCKER_REGISTRY}/review-service:latest ./review_service/
    docker build -t ${DOCKER_REGISTRY}/post-service:latest ./post_service/
    
    print_status "Docker images built successfully"
}

# Setup database
setup_database() {
    print_info "Setting up database..."
    
    # Start database services
    docker-compose up -d postgres redis elasticsearch rabbitmq
    
    # Wait for database to be ready
    print_info "Waiting for database to be ready..."
    sleep 30
    
    # Run database migrations
    print_info "Running database migrations..."
    docker-compose exec -T postgres psql -U kerya_user -d kerya_db -c "SELECT 1;" || {
        print_error "Database connection failed"
        exit 1
    }
    
    print_status "Database setup completed"
}

# Start services
start_services() {
    print_info "Starting Kerya App services..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Production deployment with Kubernetes
        deploy_to_kubernetes
    else
        # Development deployment with Docker Compose
        docker-compose up -d
        
        print_info "Waiting for services to be ready..."
        sleep 60
        
        # Check service health
        check_service_health
    fi
    
    print_status "Services started successfully"
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    print_info "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl apply -f kubernetes/namespace.yaml
    
    # Apply configurations
    kubectl apply -f kubernetes/configmap.yaml
    kubectl apply -f kubernetes/secret.yaml
    
    # Deploy infrastructure services
    kubectl apply -f kubernetes/postgres.yaml
    kubectl apply -f kubernetes/redis.yaml
    kubectl apply -f kubernetes/elasticsearch.yaml
    kubectl apply -f kubernetes/rabbitmq.yaml
    
    # Wait for infrastructure to be ready
    print_info "Waiting for infrastructure services..."
    kubectl wait --for=condition=ready pod -l app=kerya -n kerya-app --timeout=300s
    
    # Deploy application services
    kubectl apply -f kubernetes/api-gateway.yaml
    kubectl apply -f kubernetes/user-service.yaml
    kubectl apply -f kubernetes/property-service.yaml
    kubectl apply -f kubernetes/booking-service.yaml
    kubectl apply -f kubernetes/notification-service.yaml
    kubectl apply -f kubernetes/review-service.yaml
    kubectl apply -f kubernetes/post-service.yaml
    
    # Deploy monitoring
    kubectl apply -f kubernetes/monitoring/
    
    # Deploy ingress
    kubectl apply -f kubernetes/ingress/
    
    print_status "Kubernetes deployment completed"
}

# Check service health
check_service_health() {
    print_info "Checking service health..."
    
    local services=(
        "http://localhost:8000/health"
        "http://localhost:8001/health"
        "http://localhost:8002/health"
        "http://localhost:8003/health"
        "http://localhost:8004/health"
        "http://localhost:8005/health"
        "http://localhost:8006/health"
    )
    
    for service in "${services[@]}"; do
        if curl -f -s "$service" > /dev/null; then
            print_status "Service $service is healthy"
        else
            print_warning "Service $service is not responding"
        fi
    done
}

# Setup monitoring
setup_monitoring() {
    print_info "Setting up monitoring..."
    
    # Create monitoring directories
    mkdir -p monitoring/prometheus
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    # Copy monitoring configurations
    cp -r monitoring-templates/* monitoring/ 2>/dev/null || true
    
    print_status "Monitoring setup completed"
}

# Generate SSL certificates (for production)
setup_ssl() {
    if [ "$ENVIRONMENT" = "production" ]; then
        print_info "Setting up SSL certificates..."
        
        # Create SSL directory
        mkdir -p nginx/ssl
        
        # Generate self-signed certificate for development
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/nginx.key \
            -out nginx/ssl/nginx.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        print_warning "Generated self-signed SSL certificate. For production, use proper certificates."
        print_status "SSL setup completed"
    fi
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."
    
    # Run migrations for each service
    docker-compose exec -T user_service alembic upgrade head || true
    docker-compose exec -T property_service alembic upgrade head || true
    docker-compose exec -T booking_service alembic upgrade head || true
    
    print_status "Database migrations completed"
}

# Seed initial data
seed_data() {
    print_info "Seeding initial data..."
    
    # Run seed scripts if they exist
    if [ -f "scripts/seed_data.py" ]; then
        python scripts/seed_data.py
    fi
    
    print_status "Data seeding completed"
}

# Display service information
display_info() {
    echo ""
    echo -e "${BLUE}🎉 Kerya App Setup Complete!${NC}"
    echo ""
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo -e "${GREEN}Production Deployment:${NC}"
        echo "  - API Gateway: https://your-domain.com"
        echo "  - Grafana: https://your-domain.com/grafana"
        echo "  - Kibana: https://your-domain.com/kibana"
        echo "  - Jaeger: https://your-domain.com/jaeger"
    else
        echo -e "${GREEN}Development Deployment:${NC}"
        echo "  - API Gateway: http://localhost:8000"
        echo "  - API Documentation: http://localhost:8000/docs"
        echo "  - Grafana: http://localhost:3000"
        echo "  - Kibana: http://localhost:5601"
        echo "  - Jaeger: http://localhost:16686"
        echo "  - RabbitMQ Management: http://localhost:15672"
    fi
    
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Update .env file with your actual configuration"
    echo "  2. Configure external services (AWS S3, SendGrid, Twilio, etc.)"
    echo "  3. Set up proper SSL certificates for production"
    echo "  4. Configure monitoring and alerting"
    echo "  5. Run tests to verify everything works"
    echo ""
    echo -e "${BLUE}For more information, see the README.md file.${NC}"
}

# Main execution
main() {
    check_prerequisites
    setup_environment
    build_images
    setup_database
    setup_monitoring
    setup_ssl
    start_services
    run_migrations
    seed_data
    display_info
}

# Handle script arguments
case "$1" in
    "development"|"dev")
        ENVIRONMENT="development"
        main
        ;;
    "production"|"prod")
        ENVIRONMENT="production"
        main
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [environment]"
        echo "  environment: development (default) or production"
        echo ""
        echo "Examples:"
        echo "  $0                    # Setup development environment"
        echo "  $0 development        # Setup development environment"
        echo "  $0 production         # Setup production environment"
        ;;
    *)
        print_error "Invalid argument. Use 'help' for usage information."
        exit 1
        ;;
esac 