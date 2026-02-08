# Deployment Guide

This guide covers deploying the AI Patient Support Assistant to production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [AWS Deployment](#aws-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Services
- Python 3.11+
- PostgreSQL 15+
- MongoDB 6+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

### API Keys
- OpenAI API key (for AI chat)
- AWS credentials (for lab report analysis - optional)
- Firebase credentials (for push notifications - optional)

## Local Development

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-patient-support-assistant.git
cd ai-patient-support-assistant
```

### 2. Environment Setup
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

### 3. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start Services
```bash
# Start PostgreSQL, MongoDB, Redis
docker-compose up -d postgres mongodb redis
```

### 5. Initialize Database
```bash
# Run migrations
python migrations/run_migrations.py

# Initialize MongoDB
python -m app.mongodb.init_collections
python -m app.mongodb.seed_data
```

### 6. Run Application
```bash
python run.py
```

Application will be available at `http://localhost:5000`

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Service Management

```bash
# Start specific service
docker-compose up -d backend

# Restart service
docker-compose restart backend

# View service logs
docker-compose logs -f backend
```

## AWS Deployment

### Architecture Overview

```
Internet → ALB → ECS/EKS → Backend Services
                    ↓
            RDS (PostgreSQL)
            DocumentDB (MongoDB)
            ElastiCache (Redis)
            S3 (File Storage)
```

### 1. Infrastructure Setup (Terraform)

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

### 2. Database Setup

**RDS PostgreSQL:**
```bash
# Connect to RDS
psql -h your-rds-endpoint.amazonaws.com -U admin -d patient_support

# Run migrations
python migrations/run_migrations.py
```

**DocumentDB (MongoDB):**
```bash
# Connect to DocumentDB
mongo --ssl --host your-docdb-endpoint.amazonaws.com:27017 \
      --username admin --password <password>

# Initialize collections
python -m app.mongodb.init_collections
python -m app.mongodb.seed_data
```

### 3. Application Deployment

**Using ECS:**
```bash
# Build and push Docker image
docker build -t ai-patient-support:latest backend/
docker tag ai-patient-support:latest <ecr-repo-url>:latest
docker push <ecr-repo-url>:latest

# Update ECS service
aws ecs update-service --cluster patient-support-cluster \
                       --service backend-service \
                       --force-new-deployment
```

**Using EKS:**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

### 4. Configure Load Balancer

```bash
# Create target group
aws elbv2 create-target-group \
    --name patient-support-tg \
    --protocol HTTP \
    --port 5000 \
    --vpc-id <vpc-id>

# Create load balancer
aws elbv2 create-load-balancer \
    --name patient-support-alb \
    --subnets <subnet-1> <subnet-2> \
    --security-groups <sg-id>
```

### 5. SSL/TLS Configuration

```bash
# Request certificate from ACM
aws acm request-certificate \
    --domain-name api.yourdomain.com \
    --validation-method DNS

# Add HTTPS listener to ALB
aws elbv2 create-listener \
    --load-balancer-arn <alb-arn> \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=<cert-arn> \
    --default-actions Type=forward,TargetGroupArn=<tg-arn>
```

## Environment Configuration

### Production Environment Variables

```env
# Flask
SECRET_KEY=<strong-random-key>
FLASK_ENV=production

# JWT
JWT_SECRET_KEY=<strong-random-key>

# Database
DATABASE_URL=postgresql://user:pass@rds-endpoint/dbname
MONGODB_URI=mongodb://user:pass@docdb-endpoint:27017/dbname?ssl=true
REDIS_URL=redis://elasticache-endpoint:6379/0

# OpenAI
OPENAI_API_KEY=<your-openai-key>

# AWS
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_REGION=us-east-1
AWS_S3_BUCKET=patient-support-files

# Firebase
FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json

# Application
API_RATE_LIMIT=100
MAX_FILE_SIZE_MB=10
```

### Secrets Management

**AWS Secrets Manager:**
```bash
# Store secret
aws secretsmanager create-secret \
    --name patient-support/prod/db-password \
    --secret-string "your-password"

# Retrieve secret
aws secretsmanager get-secret-value \
    --secret-id patient-support/prod/db-password
```

**Environment Variables in ECS:**
```json
{
  "secrets": [
    {
      "name": "DATABASE_URL",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-url"
    }
  ]
}
```

## Database Setup

### PostgreSQL Migrations

```bash
# Run all migrations
python migrations/run_migrations.py

# Check migration status
psql -h <host> -U <user> -d <db> -c "SELECT * FROM schema_migrations;"
```

### MongoDB Initialization

```bash
# Initialize collections with validation
python -m app.mongodb.init_collections

# Seed medical knowledge data
python -m app.mongodb.seed_data

# Verify collections
mongo <connection-string> --eval "db.getCollectionNames()"
```

### Database Backups

**PostgreSQL:**
```bash
# Backup
pg_dump -h <host> -U <user> -d <db> > backup.sql

# Restore
psql -h <host> -U <user> -d <db> < backup.sql
```

**MongoDB:**
```bash
# Backup
mongodump --uri="<connection-string>" --out=backup/

# Restore
mongorestore --uri="<connection-string>" backup/
```

## Monitoring

### Application Monitoring

**CloudWatch Logs:**
```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/patient-support

# View logs
aws logs tail /ecs/patient-support --follow
```

**CloudWatch Metrics:**
- CPU utilization
- Memory utilization
- Request count
- Error rate
- Response time

### Health Checks

```bash
# Application health
curl https://api.yourdomain.com/health

# Database health
curl https://api.yourdomain.com/health/db
```

### Alerts

Configure CloudWatch alarms for:
- High error rate (> 5%)
- High response time (> 3s)
- Low memory (< 20%)
- Failed health checks

## Scaling

### Horizontal Scaling

**ECS Auto Scaling:**
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/cluster/service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --policy-name cpu-scaling \
    --service-namespace ecs \
    --resource-id service/cluster/service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### Database Scaling

**RDS:**
- Enable Multi-AZ for high availability
- Use read replicas for read-heavy workloads
- Enable auto-scaling for storage

**DocumentDB:**
- Add replica instances
- Enable auto-scaling

## Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] Security groups configured
- [ ] Secrets stored in Secrets Manager
- [ ] Database encryption enabled
- [ ] Backup strategy implemented
- [ ] Monitoring and alerts configured
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] Security headers enabled
- [ ] Regular security audits scheduled

## Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check security groups
# Verify connection string
# Test connectivity
telnet <db-host> <port>
```

**High Memory Usage:**
```bash
# Check application logs
# Monitor memory metrics
# Increase instance size if needed
```

**Slow Response Times:**
```bash
# Check database query performance
# Enable Redis caching
# Review application logs
# Scale horizontally
```

### Logs

```bash
# Application logs
docker-compose logs -f backend

# Database logs
# Check CloudWatch or RDS logs

# System logs
journalctl -u patient-support -f
```

## Rollback Procedure

### ECS Deployment Rollback

```bash
# List task definitions
aws ecs list-task-definitions --family-prefix backend

# Update service to previous version
aws ecs update-service \
    --cluster patient-support-cluster \
    --service backend-service \
    --task-definition backend:previous-version
```

### Database Rollback

```bash
# Restore from backup
psql -h <host> -U <user> -d <db> < backup.sql
```

## Performance Optimization

### Caching Strategy

- Enable Redis for session storage
- Cache medical knowledge queries
- Cache symptom autocomplete results
- Set appropriate TTL values

### Database Optimization

- Add indexes for frequently queried fields
- Use connection pooling
- Enable query caching
- Regular VACUUM and ANALYZE

### CDN Configuration

- Use CloudFront for static assets
- Enable compression
- Set cache headers

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check system health
- Review metrics

**Weekly:**
- Review performance metrics
- Check disk usage
- Update dependencies (if needed)

**Monthly:**
- Security patches
- Database maintenance
- Backup verification
- Cost optimization review

## Support

For deployment issues:
- Check logs first
- Review this guide
- Open GitHub issue
- Email: support@example.com

---

**Last Updated:** 2024
**Version:** 1.0
