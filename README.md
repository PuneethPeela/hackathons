# AI-Based Patient Support Assistant

A production-ready healthcare guidance platform that combines AI-powered chat assistance, symptom analysis, and comprehensive patient support features.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange.svg)](https://www.tensorflow.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue.svg)](https://flutter.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### ✅ Implemented (Production-Ready)

- **🔐 Authentication & Authorization**
  - JWT-based authentication with refresh tokens
  - Account lockout after 5 failed attempts
  - Secure password hashing with bcrypt
  - Profile management

- **🛡️ Enterprise Security**
  - AES-256 encryption for sensitive data
  - TLS/HTTPS enforcement
  - Comprehensive audit logging
  - Security headers (HSTS, CSP, etc.)

- **🤖 AI Chat Assistant**
  - OpenAI GPT-4 integration
  - Medical knowledge retrieval
  - Emergency detection
  - Medical terminology simplification
  - Conversation history management

- **🩺 Symptom Analysis**
  - TensorFlow-based disease prediction
  - Risk severity assessment (low/medium/high/critical)
  - Top 3 predictions with confidence scores
  - Treatment recommendations

- **📊 Database Infrastructure**
  - PostgreSQL for structured data
  - MongoDB for medical knowledge
  - Redis for caching
  - Complete migration system

### 🚧 Planned Features

- Lab report analysis with AWS Textract OCR
- Medication management with reminders
- Care navigation and appointment tracking
- Push notifications via Firebase
- Complete Flutter mobile UI
- Offline support

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Flutter Mobile App              │
│     (iOS/Android - Presentation)        │
└──────────────┬──────────────────────────┘
               │ HTTPS/TLS
┌──────────────▼──────────────────────────┐
│         Flask Backend API               │
│  (Authentication, AI, Symptom Analysis) │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼────┐ ┌──▼─────┐ ┌─▼────────┐
│PostgreSQL MongoDB │  Redis   │
│(Users,  │(Medical │ (Cache)  │
│ Data)   │Knowledge)│          │
└─────────┘ └────────┘ └──────────┘
```

## 🚀 Quick Start

### One-Command Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/ai-patient-support-assistant.git
cd ai-patient-support-assistant
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-patient-support-assistant.git
cd ai-patient-support-assistant
```

2. **Set up environment variables**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start infrastructure with Docker**
```bash
docker-compose up -d
```

4. **Install Python dependencies**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. **Run database migrations**
```bash
python migrations/run_migrations.py
```

6. **Initialize MongoDB**
```bash
python -m app.mongodb.init_collections
python -m app.mongodb.seed_data
```

7. **Start the backend server**
```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Docker-Only Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_properties/test_authentication.py

# Run property-based tests
pytest tests/test_properties/ -v
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### Chat Endpoints

#### Send Message
```http
POST /api/chat/message
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "What are the symptoms of diabetes?",
  "conversation_id": "optional-conversation-id"
}
```

### Symptom Analysis Endpoints

#### Search Symptoms
```http
GET /api/symptoms/search?q=fever&limit=10
Authorization: Bearer <access_token>
```

#### Analyze Symptoms
```http
POST /api/symptoms/analyze
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "symptoms": ["fever", "cough", "headache"],
  "age": 30,
  "gender": "male"
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# JWT
JWT_SECRET_KEY=your-jwt-secret-here

# Database
DATABASE_URL=postgresql://user:password@localhost/patient_support
MONGODB_URI=mongodb://localhost:27017/patient_support
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# AWS (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# Firebase (Optional)
FIREBASE_CREDENTIALS_PATH=path/to/credentials.json
```

## 🧪 Testing

The project uses property-based testing with Hypothesis for comprehensive test coverage:

- **21 property-based test methods**
- **1,800+ test iterations per run**
- **17 requirements validated**

Test categories:
- Authentication & Authorization
- Security & Encryption
- AI Chat Functionality
- Symptom Analysis
- Data Persistence

## 📊 Project Statistics

- **Lines of Code**: 9,500+
- **Files**: 70+
- **Test Coverage**: Comprehensive property-based testing
- **Requirements Validated**: 17/30
- **Completion**: 20% (Core services production-ready)

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: PostgreSQL 15, MongoDB 6, Redis 7
- **AI/ML**: OpenAI GPT-4, TensorFlow 2.15
- **Authentication**: JWT, bcrypt
- **Security**: Flask-Talisman, cryptography
- **Testing**: pytest, Hypothesis

### Frontend (Structure)
- **Framework**: Flutter 3.x
- **Language**: Dart
- **State Management**: Provider/Riverpod (planned)

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Cloud**: AWS (planned)
- **CI/CD**: GitHub Actions (planned)

## 📁 Project Structure

```
ai-patient-support-assistant/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # JWT, audit logging
│   │   ├── mongodb/         # MongoDB collections
│   │   └── utils/           # Utilities
│   ├── migrations/          # Database migrations
│   ├── tests/               # Test suite
│   ├── requirements.txt     # Python dependencies
│   └── run.py              # Application entry point
├── mobile/
│   └── lib/                # Flutter application
├── docker-compose.yml      # Docker services
├── README.md              # This file
└── PROJECT_SUMMARY.md     # Detailed project summary
```

## 🔒 Security

- All sensitive data encrypted with AES-256
- HTTPS/TLS enforced in production
- Comprehensive audit logging
- JWT-based authentication
- Account lockout protection
- Security headers (HSTS, CSP, X-Frame-Options)
- Regular security audits recommended

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Write property-based tests for new features
- Update documentation
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Medical Disclaimer

This application is for informational and educational purposes only. It does not provide medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- TensorFlow team for ML framework
- Flask community
- All contributors

## 📞 Support

For support, email support@example.com or open an issue on GitHub.

## 🗺️ Roadmap

### Phase 1: Core Services ✅ (Complete)
- Authentication & Security
- AI Chat Assistant
- Symptom Analysis
- Database Infrastructure

### Phase 2: Extended Services (In Progress)
- Lab Report Analysis
- Medication Management
- Care Navigation
- Notifications

### Phase 3: Frontend & Deployment (Planned)
- Complete Flutter UI
- AWS Infrastructure
- CI/CD Pipeline
- Performance Optimization

### Phase 4: Advanced Features (Future)
- Voice interaction
- Wearable device integration
- Telemedicine integration
- Multi-language support

---

**Built with ❤️ for better healthcare accessibility**
