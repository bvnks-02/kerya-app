# Kerya App Deployment Guide

## Overview

This guide covers deploying the Kerya App back-end across different environments, from local development to production. The application supports multiple deployment strategies including Docker Compose for development and Kubernetes for production.

## Prerequisites

### Development Environment
- Docker Desktop (v20.10+)
- Docker Compose (v2.0+)
- Git
- Python 3.9+ (for local development)

### Production Environment
- Kubernetes cluster (v1.24+)
- kubectl (v1.24+)
- Helm (v3.8+) - optional
- Container registry access
- SSL certificates
- Domain name

### Infrastructure Requirements

#### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Network**: 100 Mbps

#### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 500GB+ SSD
- **Network**: 1 Gbps

## Local Development Deployment

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/kerya-app.git
   cd kerya-app/server
   ```

2. **Run the setup script**:
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh development
   ```

3. **Access the application**:
   - API Gateway: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Grafana: http://localhost:3000
   - Kibana: http://localhost:5601

### Manual Setup

1. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

2. **Build and start services**:
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**:
   ```bash
   docker-compose exec user_service alembic upgrade head
   docker-compose exec property_service alembic upgrade head
   docker-compose exec booking_service alembic upgrade head
   ```

4. **Seed initial data** (optional):
   ```bash
   python scripts/seed_data.py
   ```

### Development Workflow

1. **Start development environment**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f user_service
   ```

3. **Restart a service**:
   ```bash
   docker-compose restart user_service
   ```

4. **Stop all services**:
   ```bash
   docker-compose down
   ```

## Staging Environment Deployment

### Using Docker Compose

1. **Create staging configuration**:
   ```bash
   cp env.example .env.staging
   # Edit .env.staging with staging values
   ```

2. **Deploy with staging config**:
   ```bash
   docker-compose --env-file .env.staging up -d
   ```

### Using Kubernetes

1. **Create staging namespace**:
   ```bash
   kubectl create namespace kerya-staging
   ```

2. **Apply staging configurations**:
   ```bash
   kubectl apply -f kubernetes/staging/
   ```

3. **Deploy services**:
   ```bash
   kubectl apply -f kubernetes/staging/ -n kerya-staging
   ```

## Production Deployment

### Kubernetes Deployment

#### 1. Prepare the Cluster

1. **Create namespace**:
   ```bash
   kubectl apply -f kubernetes/namespace.yaml
   ```

2. **Create secrets**:
   ```bash
   # Update kubernetes/secret.yaml with real values
   kubectl apply -f kubernetes/secret.yaml
   ```

3. **Apply configurations**:
   ```bash
   kubectl apply -f kubernetes/configmap.yaml
   ```

#### 2. Deploy Infrastructure

1. **Deploy database**:
   ```bash
   kubectl apply -f kubernetes/postgres.yaml
   kubectl apply -f kubernetes/redis.yaml
   kubectl apply -f kubernetes/elasticsearch.yaml
   kubectl apply -f kubernetes/rabbitmq.yaml
   ```

2. **Wait for infrastructure readiness**:
   ```bash
   kubectl wait --for=condition=ready pod -l app=kerya -n kerya-app --timeout=300s
   ```

#### 3. Deploy Application Services

1. **Deploy API Gateway**:
   ```bash
   kubectl apply -f kubernetes/api-gateway.yaml
   ```

2. **Deploy microservices**:
   ```bash
   kubectl apply -f kubernetes/user-service.yaml
   kubectl apply -f kubernetes/property-service.yaml
   kubectl apply -f kubernetes/booking-service.yaml
   kubectl apply -f kubernetes/notification-service.yaml
   kubectl apply -f kubernetes/review-service.yaml
   kubectl apply -f kubernetes/post-service.yaml
   ```

#### 4. Deploy Monitoring

1. **Deploy monitoring stack**:
   ```bash
   kubectl apply -f kubernetes/monitoring/
   ```

2. **Deploy ingress**:
   ```bash
   kubectl apply -f kubernetes/ingress/
   ```

### Using Helm (Alternative)

1. **Add Helm repository**:
   ```bash
   helm repo add kerya https://charts.kerya.com
   helm repo update
   ```

2. **Install Kerya App**:
   ```bash
   helm install kerya-app kerya/kerya-app \
     --namespace kerya-app \
     --create-namespace \
     --values values-production.yaml
   ```

## Configuration Management

### Environment Variables

#### Required Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# JWT
JWT_SECRET_KEY=your_secret_key

# External Services
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
SENDGRID_API_KEY=your_sendgrid_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

#### Optional Variables
```bash
# Monitoring
PROMETHEUS_ENABLED=true
JAEGER_ENABLED=true

# Security
CORS_ORIGINS=https://app.kerya.com
RATE_LIMIT_REQUESTS=100

# Business Logic
POINTS_REGISTRATION_BONUS=100
MAX_BOOKING_DAYS=30
```

### Configuration Files

#### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kerya-config
data:
  APP_NAME: "Kerya App"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
```

#### Kubernetes Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kerya-secrets
type: Opaque
data:
  JWT_SECRET_KEY: <base64-encoded>
  DATABASE_PASSWORD: <base64-encoded>
```

## SSL/TLS Configuration

### Using Let's Encrypt

1. **Install cert-manager**:
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml
   ```

2. **Create ClusterIssuer**:
   ```yaml
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: admin@kerya.com
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
       - http01:
           ingress:
             class: nginx
   ```

3. **Apply to ingress**:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     annotations:
       cert-manager.io/cluster-issuer: "letsencrypt-prod"
   spec:
     tls:
     - hosts:
       - api.kerya.com
       secretName: kerya-tls
   ```

### Using Custom Certificates

1. **Create TLS secret**:
   ```bash
   kubectl create secret tls kerya-tls \
     --cert=path/to/cert.pem \
     --key=path/to/key.pem \
     -n kerya-app
   ```

2. **Reference in ingress**:
   ```yaml
   spec:
     tls:
     - hosts:
       - api.kerya.com
       secretName: kerya-tls
   ```

## Monitoring and Observability

### Prometheus Configuration

1. **Create Prometheus config**:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: prometheus-config
   data:
     prometheus.yml: |
       global:
         scrape_interval: 15s
       scrape_configs:
       - job_name: 'kerya-app'
         static_configs:
         - targets: ['kerya-api-gateway:8000']
   ```

2. **Deploy Prometheus**:
   ```bash
   kubectl apply -f kubernetes/monitoring/prometheus.yaml
   ```

### Grafana Dashboards

1. **Create dashboard config**:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: grafana-dashboards
   data:
     kerya-dashboard.json: |
       {
         "dashboard": {
           "title": "Kerya App Metrics",
           "panels": [...]
         }
       }
   ```

2. **Deploy Grafana**:
   ```bash
   kubectl apply -f kubernetes/monitoring/grafana.yaml
   ```

### Logging Configuration

1. **Deploy Elasticsearch**:
   ```bash
   kubectl apply -f kubernetes/monitoring/elasticsearch.yaml
   ```

2. **Deploy Kibana**:
   ```bash
   kubectl apply -f kubernetes/monitoring/kibana.yaml
   ```

3. **Configure log shipping**:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: fluentd-config
   data:
     fluent.conf: |
       <source>
         @type tail
         path /var/log/containers/*.log
         pos_file /var/log/fluentd-containers.log.pos
         tag kubernetes.*
         read_from_head true
         <parse>
           @type json
           time_format %Y-%m-%dT%H:%M:%S.%NZ
         </parse>
       </source>
   ```

## Backup and Recovery

### Database Backup

1. **Create backup job**:
   ```yaml
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: postgres-backup
   spec:
     schedule: "0 2 * * *"
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: backup
               image: postgres:15
               command:
               - /bin/bash
               - -c
               - |
                 pg_dump $DATABASE_URL > /backup/backup-$(date +%Y%m%d).sql
               env:
               - name: DATABASE_URL
                 valueFrom:
                   secretKeyRef:
                     name: kerya-secrets
                     key: DATABASE_URL
             volumes:
             - name: backup-storage
               persistentVolumeClaim:
                 claimName: backup-pvc
   ```

2. **Create backup PVC**:
   ```yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: backup-pvc
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 100Gi
   ```

### Disaster Recovery

1. **Create recovery script**:
   ```bash
   #!/bin/bash
   # Restore database
   kubectl exec -it kerya-postgres-0 -- psql -U kerya_user -d kerya_db < backup.sql
   
   # Restart services
   kubectl rollout restart deployment/kerya-api-gateway
   kubectl rollout restart deployment/kerya-user-service
   ```

2. **Test recovery procedure**:
   ```bash
   # Create test backup
   kubectl exec -it kerya-postgres-0 -- pg_dump -U kerya_user kerya_db > test-backup.sql
   
   # Restore to test database
   kubectl exec -it kerya-postgres-0 -- psql -U kerya_user -d kerya_test < test-backup.sql
   ```

## Scaling and Performance

### Horizontal Pod Autoscaling

1. **Create HPA for API Gateway**:
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: kerya-api-gateway-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: kerya-api-gateway
     minReplicas: 3
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
     - type: Resource
       resource:
         name: memory
         target:
           type: Utilization
           averageUtilization: 80
   ```

2. **Create HPA for services**:
   ```bash
   kubectl apply -f kubernetes/scaling/
   ```

### Database Scaling

1. **Read replicas**:
   ```yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: postgres-replica
   spec:
     replicas: 3
     serviceName: postgres-replica
     template:
       spec:
         containers:
         - name: postgres
           image: postgres:15
           env:
           - name: POSTGRES_DB
             value: kerya_db
           - name: POSTGRES_USER
             value: kerya_user
           - name: POSTGRES_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: kerya-secrets
                 key: DATABASE_PASSWORD
   ```

2. **Connection pooling**:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: pgbouncer
   spec:
     replicas: 2
     template:
       spec:
         containers:
         - name: pgbouncer
           image: pgbouncer/pgbouncer:latest
           ports:
           - containerPort: 5432
   ```

## Security Hardening

### Network Policies

1. **Create network policy**:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: kerya-network-policy
   spec:
     podSelector:
       matchLabels:
         app: kerya
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - namespaceSelector:
           matchLabels:
             name: ingress-nginx
       ports:
       - protocol: TCP
         port: 8000
     egress:
     - to:
       - namespaceSelector:
           matchLabels:
             name: kerya-app
       ports:
       - protocol: TCP
         port: 5432
   ```

### Pod Security Standards

1. **Create Pod Security Policy**:
   ```yaml
   apiVersion: policy/v1
   kind: PodSecurityPolicy
   metadata:
     name: kerya-psp
   spec:
     privileged: false
     allowPrivilegeEscalation: false
     requiredDropCapabilities:
     - ALL
     volumes:
     - 'configMap'
     - 'emptyDir'
     - 'projected'
     - 'secret'
     - 'downwardAPI'
     - 'persistentVolumeClaim'
     hostNetwork: false
     hostIPC: false
     hostPID: false
     runAsUser:
       rule: 'MustRunAsNonRoot'
     seLinux:
       rule: 'RunAsAny'
     supplementalGroups:
       rule: 'MustRunAs'
       ranges:
       - min: 1
         max: 65535
     fsGroup:
       rule: 'MustRunAs'
       ranges:
       - min: 1
         max: 65535
     readOnlyRootFilesystem: true
   ```

### RBAC Configuration

1. **Create service accounts**:
   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: kerya-user-service
     namespace: kerya-app
   ---
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: kerya-api-gateway
     namespace: kerya-app
   ```

2. **Create roles and bindings**:
   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     name: kerya-service-role
     namespace: kerya-app
   rules:
   - apiGroups: [""]
     resources: ["configmaps", "secrets"]
     verbs: ["get", "list", "watch"]
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: RoleBinding
   metadata:
     name: kerya-service-rolebinding
     namespace: kerya-app
   subjects:
   - kind: ServiceAccount
     name: kerya-user-service
     namespace: kerya-app
   roleRef:
     kind: Role
     name: kerya-service-role
     apiGroup: rbac.authorization.k8s.io
   ```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database status
kubectl get pods -n kerya-app -l app=postgres

# Check database logs
kubectl logs -f kerya-postgres-0 -n kerya-app

# Test database connection
kubectl exec -it kerya-postgres-0 -n kerya-app -- psql -U kerya_user -d kerya_db -c "SELECT 1;"
```

#### 2. Service Health Issues
```bash
# Check service status
kubectl get pods -n kerya-app

# Check service logs
kubectl logs -f deployment/kerya-user-service -n kerya-app

# Check service health endpoint
kubectl port-forward svc/kerya-user-service 8001:8001 -n kerya-app
curl http://localhost:8001/health
```

#### 3. Resource Issues
```bash
# Check resource usage
kubectl top pods -n kerya-app

# Check events
kubectl get events -n kerya-app --sort-by='.lastTimestamp'

# Check node resources
kubectl top nodes
```

### Debug Commands

```bash
# Get all resources in namespace
kubectl get all -n kerya-app

# Describe specific resource
kubectl describe pod kerya-user-service-xyz -n kerya-app

# Execute command in pod
kubectl exec -it kerya-user-service-xyz -n kerya-app -- /bin/bash

# Port forward for debugging
kubectl port-forward svc/kerya-api-gateway 8000:80 -n kerya-app
```

## Maintenance

### Regular Maintenance Tasks

1. **Update dependencies**:
   ```bash
   # Update Python packages
   pip install --upgrade -r requirements.txt
   
   # Update Docker images
   docker pull kerya/user-service:latest
   docker pull kerya/api-gateway:latest
   ```

2. **Database maintenance**:
   ```bash
   # Vacuum database
   kubectl exec -it kerya-postgres-0 -n kerya-app -- psql -U kerya_user -d kerya_db -c "VACUUM ANALYZE;"
   
   # Check database size
   kubectl exec -it kerya-postgres-0 -n kerya-app -- psql -U kerya_user -d kerya_db -c "SELECT pg_size_pretty(pg_database_size('kerya_db'));"
   ```

3. **Log rotation**:
   ```bash
   # Clean old logs
   kubectl exec -it kerya-elasticsearch-0 -n kerya-app -- curl -X DELETE "localhost:9200/logs-$(date -d '30 days ago' +%Y.%m.%d)"
   ```

### Performance Monitoring

1. **Monitor key metrics**:
   - API response times
   - Database query performance
   - Memory and CPU usage
   - Error rates
   - User activity

2. **Set up alerts**:
   ```yaml
   apiVersion: monitoring.coreos.com/v1alpha1
   kind: PrometheusRule
   metadata:
     name: kerya-alerts
   spec:
     groups:
     - name: kerya.rules
       rules:
       - alert: HighErrorRate
         expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
         for: 5m
         labels:
           severity: warning
         annotations:
           summary: High error rate detected
   ```

This deployment guide provides comprehensive instructions for deploying the Kerya App across different environments. Follow the sections relevant to your deployment strategy and ensure all prerequisites are met before proceeding. 