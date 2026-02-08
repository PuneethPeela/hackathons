# Quick Reference Guide

Essential commands and information for the AI Patient Support Assistant.

## 🚀 Quick Start

```bash
# One-command setup
./setup.sh

# Or manual setup
docker-compose up -d
cd backend && python run.py
```

## 📡 API Endpoints

### Authentication
```bash
# Register
POST /api/auth/register

# Login
POST /api/auth/login

# Get Profile
GET /api/auth/profile
```

### Chat
```bash
# Send Message
POST /api/chat/message

# Get History
GET /api/chat/history/{id}

# List Conversations
GET /api/chat/conversations
```

### Symptoms
```bash
# Search
GET /api/symptoms/search?q=fever

# Analyze
POST /api/symptoms/analyze

# History
GET /api/symptoms/history
```

## 🔑 Environment Variables

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:pass@localhost/db
MONGODB_URI=mongodb://localhost:27017/db
OPENAI_API_KEY=your-openai-key
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Rebuild
docker-compose build
```

## 🗄️ Database Commands

```bash
# Run migrations
python migrations/run_migrations.py

# Initialize MongoDB
python -m app.mongodb.init_collections
python -m app.mongodb.seed_data

# Backup PostgreSQL
pg_dump -h localhost -U user db > backup.sql

# Backup MongoDB
mongodump --uri="mongodb://localhost:27017/db"
```

## 🧪 Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_properties/test_authentication.py

# Run with verbose output
pytest -v

# Run property tests only
pytest tests/test_properties/
```

## 🔍 Debugging

```bash
# Check logs
docker-compose logs -f backend

# Check database connection
psql -h localhost -U user -d db

# Check MongoDB connection
mongo mongodb://localhost:27017/db

# Check Redis connection
redis-cli ping

# Test API endpoint
curl http://localhost:5000/health
```

## 📊 Monitoring

```bash
# Check running containers
docker-compose ps

# Check resource usage
docker stats

# Check disk usage
docker system df

# View application logs
tail -f backend/logs/app.log
```

## 🔒 Security

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check for secrets in code
git secrets --scan

# Run security scan
bandit -r app/

# Check dependencies
safety check
```

## 📦 Dependency Management

```bash
# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip list --outdated

# Freeze dependencies
pip freeze > requirements.txt

# Check for vulnerabilities
safety check
```

## 🚢 Deployment

```bash
# Build Docker image
docker build -t ai-patient-support:latest backend/

# Tag for registry
docker tag ai-patient-support:latest registry/ai-patient-support:latest

# Push to registry
docker push registry/ai-patient-support:latest

# Deploy to production
# (Configure based on your infrastructure)
```

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection
psql -h localhost -U user -d db -c "SELECT 1"

# Restart database
docker-compose restart postgres
```

### MongoDB Issues
```bash
# Check if MongoDB is running
docker-compose ps mongodb

# Check connection
mongo mongodb://localhost:27017/db --eval "db.stats()"

# Restart MongoDB
docker-compose restart mongodb
```

### Application Errors
```bash
# Check logs
docker-compose logs -f backend

# Check Python errors
python -m py_compile app/*.py

# Run in debug mode
FLASK_ENV=development python run.py
```

## 📝 Common Tasks

### Add New User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "male"
  }'
```

### Test AI Chat
```bash
# First login to get token
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}' \
  | jq -r '.access_token')

# Send message
curl -X POST http://localhost:5000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the symptoms of diabetes?"}'
```

### Analyze Symptoms
```bash
curl -X POST http://localhost:5000/api/symptoms/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough", "headache"],
    "age": 30,
    "gender": "male"
  }'
```

## 📚 Documentation Links

- [README.md](README.md) - Project overview
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [SECURITY_IMPLEMENTATION.md](backend/SECURITY_IMPLEMENTATION.md) - Security details

## 🆘 Getting Help

1. Check documentation
2. Search existing issues on GitHub
3. Ask in GitHub Discussions
4. Email: support@example.com

## 📊 Project Statistics

- **Lines of Code**: 9,500+
- **Files**: 70+
- **Tests**: 21 property-based tests
- **Requirements Validated**: 17/30
- **Completion**: 20% (Core services)

## 🎯 Key Features

- ✅ JWT Authentication
- ✅ AES-256 Encryption
- ✅ AI Chat (OpenAI GPT-4)
- ✅ Symptom Analysis (TensorFlow)
- ✅ Risk Assessment
- ✅ Medical Knowledge Base
- ✅ Audit Logging
- ✅ TLS/HTTPS

## ⚡ Performance

- Response Time: <3 seconds (AI chat)
- Rate Limit: 100 requests/minute
- Database: PostgreSQL + MongoDB + Redis
- Caching: Redis-based

## 🔐 Security Features

- JWT tokens (15min access, 7 days refresh)
- Account lockout (5 failed attempts)
- AES-256 encryption
- HTTPS/TLS enforcement
- Security headers (HSTS, CSP)
- Comprehensive audit logging

---

**Quick Reference Version**: 1.0.0
**Last Updated**: 2024
