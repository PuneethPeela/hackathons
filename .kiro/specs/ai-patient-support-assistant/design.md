# Design Document

## Overview

The AI-Based Patient Support Assistant is a production-ready healthcare guidance platform that combines modern mobile development (Flutter), robust backend services (Python Flask), advanced AI capabilities (OpenAI, HuggingFace, TensorFlow), and enterprise-grade infrastructure (AWS, Docker). The system architecture follows microservices principles with clear separation between presentation, business logic, AI processing, and data persistence layers.

The platform enables patients to:
- Interact with an AI assistant for medical guidance
- Analyze symptoms and understand possible conditions
- Upload and interpret lab reports
- Manage medications with automated reminders
- Navigate their healthcare journey with appointment tracking

Key design principles:
- **Security-first**: All patient data encrypted at rest and in transit
- **Scalability**: Horizontal scaling with load balancing and autoscaling
- **Ethical AI**: Transparent confidence scores and medical disclaimers
- **Responsive design**: Cross-platform mobile experience
- **High availability**: Fault-tolerant architecture with 99.9% uptime target

## Architecture

### System Architecture Overview

The system follows a layered microservices architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     Flutter Mobile App                       │
│  (iOS/Android - Presentation Layer)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/TLS 1.3
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              AWS Application Load Balancer                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────────┐ ┌─▼──────────────┐
│   Auth API   │ │  Core API  │ │   AI Service   │
│   (Flask)    │ │  (Flask)   │ │   (Flask)      │
└──────┬───────┘ └─────┬──────┘ └────┬───────────┘
       │               │              │
       │         ┌─────┴──────┐       │
       │         │            │       │
┌──────▼─────┐ ┌▼──────────┐ │  ┌────▼──────────┐
│ PostgreSQL │ │  MongoDB  │ │  │  AI Models    │
│  (Users,   │ │ (Medical  │ │  │ (TensorFlow,  │
│   Meds,    │ │Knowledge) │ │  │  OpenAI)      │
│   Appts)   │ │           │ │  │               │
└────────────┘ └───────────┘ │  └───────────────┘
                              │
                         ┌────▼──────────┐
                         │ AWS Textract  │
                         │  (OCR)        │
                         └───────────────┘
                              
┌─────────────────────────────────────────┐
│   Firebase Cloud Messaging (FCM)        │
│   (Push Notifications)                  │
└─────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- Flutter 3.x (Dart)
- Provider/Riverpod for state management
- HTTP client for API communication
- Firebase SDK for push notifications
- Local storage for offline caching

**Backend:**
- Python 3.11+
- Flask 3.x with Flask-RESTful
- Flask-JWT-Extended for authentication
- SQLAlchemy for PostgreSQL ORM
- PyMongo for MongoDB access
- Gunicorn WSGI server
- Redis for caching and session management

**AI/ML:**
- OpenAI GPT-4 API for conversational AI
- HuggingFace Transformers for medical NLP
- TensorFlow 2.x for symptom prediction models
- AWS Textract for OCR
- scikit-learn for data preprocessing

**Databases:**
- PostgreSQL 15+ (structured data)
- MongoDB 6+ (unstructured medical knowledge)
- Redis 7+ (caching, sessions)

**Infrastructure:**
- Docker containers
- AWS ECS/EKS for orchestration
- AWS RDS for PostgreSQL
- AWS DocumentDB for MongoDB compatibility
- AWS S3 for file storage
- AWS CloudWatch for monitoring
- AWS Secrets Manager for credentials

**CI/CD:**
- GitHub Actions or AWS CodePipeline
- Docker Hub or AWS ECR for container registry
- Automated testing with pytest and Flutter test

## Components and Interfaces

### Frontend Components

#### 1. Authentication Module
**Responsibilities:**
- User registration and login forms
- JWT token management
- Session persistence
- Profile management UI

**Key Classes:**
- `AuthService`: Handles API calls for authentication
- `AuthProvider`: State management for user session
- `LoginScreen`: Login UI widget
- `RegisterScreen`: Registration UI widget
- `ProfileScreen`: User profile management

**Interfaces:**
```dart
abstract class IAuthService {
  Future<AuthResult> register(String email, String password, UserProfile profile);
  Future<AuthResult> login(String email, String password);
  Future<void> logout();
  Future<UserProfile> getProfile();
  Future<void> updateProfile(UserProfile profile);
}
```

#### 2. AI Chat Interface
**Responsibilities:**
- Real-time chat UI with message bubbles
- Voice input integration (optional)
- Conversation history display
- Typing indicators and loading states

**Key Classes:**
- `ChatService`: API communication for chat
- `ChatProvider`: Message state management
- `ChatScreen`: Main chat interface
- `MessageWidget`: Individual message display
- `ConversationHistory`: Historical chat view

**Interfaces:**
```dart
abstract class IChatService {
  Future<ChatMessage> sendMessage(String message, String conversationId);
  Stream<ChatMessage> streamResponse(String message);
  Future<List<ChatMessage>> getHistory(String conversationId);
}
```

#### 3. Symptom Checker Module
**Responsibilities:**
- Symptom input with autocomplete
- Multi-symptom selection
- Risk severity visualization
- Results display with confidence scores

**Key Classes:**
- `SymptomService`: API calls for symptom analysis
- `SymptomProvider`: Symptom state management
- `SymptomInputScreen`: Symptom entry UI
- `SymptomResultsScreen`: Analysis results display
- `RiskIndicator`: Visual risk level component

**Interfaces:**
```dart
abstract class ISymptomService {
  Future<List<String>> searchSymptoms(String query);
  Future<SymptomAnalysis> analyzeSymptoms(List<String> symptoms);
  Future<List<Disease>> getPossibleConditions(SymptomAnalysis analysis);
}
```

#### 4. Lab Report Module
**Responsibilities:**
- File picker for PDF/image upload
- Upload progress indication
- Report preview
- Results interpretation display

**Key Classes:**
- `LabReportService`: Upload and analysis API calls
- `LabReportProvider`: Report state management
- `UploadScreen`: File upload UI
- `ReportPreviewScreen`: Uploaded report display
- `ResultsInterpretationScreen`: Analysis results

**Interfaces:**
```dart
abstract class ILabReportService {
  Future<UploadResult> uploadReport(File file);
  Future<LabAnalysis> getAnalysis(String reportId);
  Future<List<LabReport>> getReportHistory();
}
```

#### 5. Medication Tracker Module
**Responsibilities:**
- Medication entry forms
- Schedule configuration
- Reminder management
- Adherence tracking visualization

**Key Classes:**
- `MedicationService`: Medication API calls
- `MedicationProvider`: Medication state management
- `MedicationListScreen`: All medications display
- `AddMedicationScreen`: New medication entry
- `AdherenceChart`: Visual adherence tracking

**Interfaces:**
```dart
abstract class IMedicationService {
  Future<Medication> addMedication(MedicationDetails details);
  Future<void> updateMedication(String id, MedicationDetails details);
  Future<void> recordAdherence(String medicationId, DateTime timestamp);
  Future<AdherenceReport> getAdherenceReport(String medicationId);
}
```

#### 6. Care Navigation Module
**Responsibilities:**
- Appointment scheduling forms
- Calendar view of appointments
- Treatment progress timeline
- Follow-up reminder display

**Key Classes:**
- `CareNavigationService`: Appointment API calls
- `CareProvider`: Care navigation state
- `AppointmentScreen`: Appointment management
- `TreatmentTimelineScreen`: Progress visualization
- `CalendarWidget`: Appointment calendar

**Interfaces:**
```dart
abstract class ICareNavigationService {
  Future<Appointment> scheduleAppointment(AppointmentDetails details);
  Future<List<Appointment>> getAppointments();
  Future<TreatmentProgress> getProgress();
  Future<void> updateProgress(String milestoneId, bool completed);
}
```

### Backend Components

#### 1. Authentication Service
**Responsibilities:**
- User registration with validation
- JWT token generation and validation
- Password hashing (bcrypt)
- Role-based access control

**Endpoints:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

**Key Classes:**
```python
class AuthService:
    def register_user(email: str, password: str, profile: dict) -> User
    def authenticate(email: str, password: str) -> TokenPair
    def validate_token(token: str) -> User
    def refresh_token(refresh_token: str) -> TokenPair
```

#### 2. AI Chat Service
**Responsibilities:**
- OpenAI API integration
- Conversation context management
- Medical terminology simplification
- Response streaming

**Endpoints:**
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history/{conversation_id}` - Get conversation history
- `POST /api/chat/stream` - Stream AI responses

**Key Classes:**
```python
class ChatService:
    def process_message(message: str, user_id: str, conversation_id: str) -> ChatResponse
    def get_conversation_history(conversation_id: str) -> List[Message]
    def simplify_medical_terms(text: str) -> str
```

#### 3. Symptom Analysis Service
**Responsibilities:**
- Symptom validation and autocomplete
- TensorFlow model inference
- Risk severity calculation
- Confidence scoring

**Endpoints:**
- `GET /api/symptoms/search?q={query}` - Search symptoms
- `POST /api/symptoms/analyze` - Analyze symptoms
- `GET /api/symptoms/conditions/{symptom_id}` - Get related conditions

**Key Classes:**
```python
class SymptomAnalysisService:
    def search_symptoms(query: str) -> List[Symptom]
    def analyze_symptoms(symptoms: List[str]) -> AnalysisResult
    def calculate_risk_severity(predictions: List[Prediction]) -> RiskLevel
    def get_possible_conditions(symptoms: List[str]) -> List[Disease]
```

#### 4. Lab Report Service
**Responsibilities:**
- File upload handling
- AWS Textract integration
- Data extraction and parsing
- Result interpretation

**Endpoints:**
- `POST /api/lab-reports/upload` - Upload lab report
- `GET /api/lab-reports/{report_id}` - Get report details
- `GET /api/lab-reports/{report_id}/analysis` - Get analysis
- `GET /api/lab-reports/history` - Get report history

**Key Classes:**
```python
class LabReportService:
    def upload_report(file: FileStorage, user_id: str) -> UploadResult
    def extract_data(file_path: str) -> ExtractedData
    def analyze_results(extracted_data: ExtractedData) -> LabAnalysis
    def compare_with_standards(values: dict) -> ComparisonResult
```

#### 5. Medication Management Service
**Responsibilities:**
- Medication CRUD operations
- Schedule management
- Adherence tracking
- Reminder scheduling

**Endpoints:**
- `POST /api/medications` - Add medication
- `GET /api/medications` - List medications
- `PUT /api/medications/{id}` - Update medication
- `DELETE /api/medications/{id}` - Delete medication
- `POST /api/medications/{id}/adherence` - Record adherence
- `GET /api/medications/{id}/adherence-report` - Get adherence report

**Key Classes:**
```python
class MedicationService:
    def add_medication(details: MedicationDetails, user_id: str) -> Medication
    def update_medication(medication_id: str, details: MedicationDetails) -> Medication
    def record_adherence(medication_id: str, timestamp: datetime) -> AdherenceRecord
    def calculate_adherence_score(medication_id: str) -> float
```

#### 6. Care Navigation Service
**Responsibilities:**
- Appointment management
- Treatment plan tracking
- Follow-up scheduling
- Progress monitoring

**Endpoints:**
- `POST /api/appointments` - Schedule appointment
- `GET /api/appointments` - List appointments
- `PUT /api/appointments/{id}` - Update appointment
- `GET /api/treatment/progress` - Get treatment progress
- `PUT /api/treatment/progress/{milestone_id}` - Update milestone

**Key Classes:**
```python
class CareNavigationService:
    def schedule_appointment(details: AppointmentDetails, user_id: str) -> Appointment
    def get_appointments(user_id: str) -> List[Appointment]
    def update_treatment_progress(milestone_id: str, completed: bool) -> Progress
    def schedule_followup(appointment_id: str, days_after: int) -> Appointment
```

#### 7. Notification Service
**Responsibilities:**
- Firebase Cloud Messaging integration
- Notification scheduling
- Device token management
- Notification history

**Key Classes:**
```python
class NotificationService:
    def send_notification(user_id: str, title: str, body: str, data: dict) -> bool
    def schedule_notification(user_id: str, scheduled_time: datetime, notification: Notification) -> str
    def register_device_token(user_id: str, token: str) -> bool
    def send_medication_reminder(medication_id: str) -> bool
```

### AI Processing Components

#### 1. Conversational AI Engine
**Technology:** OpenAI GPT-4 API + HuggingFace Transformers

**Responsibilities:**
- Natural language understanding
- Context-aware responses
- Medical terminology translation
- Conversation memory management

**Key Classes:**
```python
class ConversationalAI:
    def generate_response(prompt: str, context: ConversationContext) -> str
    def translate_medical_terms(text: str) -> str
    def extract_intent(message: str) -> Intent
    def maintain_context(conversation_id: str, message: str) -> ConversationContext
```

#### 2. Symptom Prediction Model
**Technology:** TensorFlow 2.x with custom neural network

**Model Architecture:**
- Input layer: Multi-hot encoded symptoms (500+ symptoms)
- Hidden layers: 3 dense layers (256, 128, 64 neurons) with ReLU activation
- Dropout layers (0.3) for regularization
- Output layer: Softmax over disease classes (200+ diseases)

**Responsibilities:**
- Symptom-to-disease prediction
- Confidence scoring
- Model versioning and updates

**Key Classes:**
```python
class SymptomPredictionModel:
    def predict(symptoms: List[str]) -> List[Prediction]
    def get_confidence_scores(predictions: np.ndarray) -> List[float]
    def load_model(version: str) -> tf.keras.Model
    def preprocess_symptoms(symptoms: List[str]) -> np.ndarray
```

#### 3. Lab Report OCR Engine
**Technology:** AWS Textract

**Responsibilities:**
- Text extraction from PDFs and images
- Table detection and parsing
- Medical value recognition
- Structured data output

**Key Classes:**
```python
class LabReportOCR:
    def extract_text(file_path: str) -> TextractResult
    def parse_tables(textract_result: TextractResult) -> List[Table]
    def extract_lab_values(tables: List[Table]) -> Dict[str, LabValue]
    def validate_extraction_accuracy(result: TextractResult) -> float
```

#### 4. Medical Knowledge Retriever
**Technology:** MongoDB with vector embeddings (optional)

**Responsibilities:**
- Disease information retrieval
- Treatment guideline lookup
- Symptom-disease mapping
- Medical standard ranges

**Key Classes:**
```python
class MedicalKnowledgeRetriever:
    def get_disease_info(disease_name: str) -> DiseaseInfo
    def get_treatment_guidelines(disease_name: str) -> TreatmentGuidelines
    def get_symptom_mapping(symptom: str) -> List[Disease]
    def get_lab_standard_ranges(test_name: str) -> ReferenceRange
```

## Data Models

### PostgreSQL Schema

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

#### Medications Table
```sql
CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(50),
    schedule_times JSONB,
    start_date DATE NOT NULL,
    end_date DATE,
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_medications_user_id ON medications(user_id);
CREATE INDEX idx_medications_active ON medications(is_active);
```

#### Adherence Records Table
```sql
CREATE TABLE adherence_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medication_id UUID REFERENCES medications(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP NOT NULL,
    taken_time TIMESTAMP,
    status VARCHAR(20) NOT NULL, -- 'taken', 'missed', 'skipped'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_adherence_medication_id ON adherence_records(medication_id);
CREATE INDEX idx_adherence_scheduled_time ON adherence_records(scheduled_time);
```

#### Appointments Table
```sql
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    appointment_date TIMESTAMP NOT NULL,
    location VARCHAR(255),
    doctor_name VARCHAR(100),
    specialty VARCHAR(100),
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled'
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_appointments_user_id ON appointments(user_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
```

#### Lab Reports Table
```sql
CREATE TABLE lab_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_date DATE,
    extracted_data JSONB,
    analysis_results JSONB,
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lab_reports_user_id ON lab_reports(user_id);
CREATE INDEX idx_lab_reports_status ON lab_reports(processing_status);
```

#### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
```

#### Symptom Analyses Table
```sql
CREATE TABLE symptom_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symptoms JSONB NOT NULL,
    predictions JSONB NOT NULL,
    risk_severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    recommended_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_symptom_analyses_user_id ON symptom_analyses(user_id);
CREATE INDEX idx_symptom_analyses_risk ON symptom_analyses(risk_severity);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

### MongoDB Collections

#### Medical Knowledge Base
```javascript
{
  "_id": ObjectId,
  "disease_name": String,
  "icd_code": String,
  "category": String,
  "description": String,
  "simple_explanation": String,
  "symptoms": [String],
  "causes": [String],
  "risk_factors": [String],
  "complications": [String],
  "prevention": [String],
  "treatment_options": [
    {
      "type": String,
      "description": String,
      "medications": [String]
    }
  ],
  "lifestyle_recommendations": [String],
  "when_to_see_doctor": [String],
  "related_conditions": [String],
  "references": [String],
  "last_updated": Date
}
```

#### Symptom Database
```javascript
{
  "_id": ObjectId,
  "symptom_name": String,
  "synonyms": [String],
  "category": String,
  "severity_indicators": [String],
  "associated_diseases": [
    {
      "disease_id": String,
      "correlation_strength": Number
    }
  ],
  "questions_to_ask": [String],
  "red_flags": [String]
}
```

#### Treatment Guidelines
```javascript
{
  "_id": ObjectId,
  "condition": String,
  "guideline_source": String,
  "publication_date": Date,
  "recommendations": [
    {
      "stage": String,
      "interventions": [String],
      "medications": [
        {
          "name": String,
          "dosage": String,
          "duration": String,
          "contraindications": [String]
        }
      ],
      "lifestyle_changes": [String],
      "monitoring": [String]
    }
  ],
  "evidence_level": String,
  "references": [String]
}
```

#### Lab Test Standards
```javascript
{
  "_id": ObjectId,
  "test_name": String,
  "test_code": String,
  "category": String,
  "unit": String,
  "reference_ranges": [
    {
      "age_group": String,
      "gender": String,
      "min_value": Number,
      "max_value": Number,
      "optimal_range": {
        "min": Number,
        "max": Number
      }
    }
  ],
  "interpretation": {
    "low": String,
    "normal": String,
    "high": String,
    "critical_low": Number,
    "critical_high": Number
  },
  "clinical_significance": String,
  "related_tests": [String]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After reviewing all testable properties from the prework, I've identified several areas where properties can be consolidated to eliminate redundancy:

**Consolidation Opportunities:**
1. Properties 1.1 and 1.4 both test data persistence round-trips (registration and profile updates)
2. Properties 2.4 and 1.5 both test data retrieval for specific users
3. Properties 8.1, 8.2, and 8.3 all test required content in AI responses
4. Properties 5.1 and 6.1 both test data persistence with round-trip validation
5. Properties 5.2 and 6.2 both test time-based notification delivery

**Consolidated Properties:**
- Combine 1.1 and 1.4 into a single "User data round-trip" property
- Combine 8.1, 8.2, and 8.3 into a comprehensive "AI response compliance" property
- Keep notification properties separate as they test different triggers

This consolidation reduces 50+ testable criteria to approximately 40 unique properties while maintaining complete coverage.

### Core Properties

**Property 1: User data round-trip consistency**
*For any* valid user registration data or profile update, storing the data then retrieving it should return equivalent values with encrypted sensitive fields
**Validates: Requirements 1.1, 1.4**

**Property 2: Authentication token generation**
*For any* valid user credentials, successful authentication should generate a valid JWT token that can be verified and decoded
**Validates: Requirements 1.2**

**Property 3: Session expiration enforcement**
*For any* expired or invalid session token, attempts to access protected resources should be rejected with authentication error
**Validates: Requirements 1.3**

**Property 4: User data isolation**
*For any* user, retrieving medical history or personal data should return only records associated with that user's ID
**Validates: Requirements 1.5**

**Property 5: AI response time constraint**
*For any* user message to the AI Chat Assistant, a response should be generated within 3 seconds
**Validates: Requirements 2.1**

**Property 6: Medical terminology simplification**
*For any* medical term in a query, the AI response should use simpler language with readability score improvement
**Validates: Requirements 2.2**

**Property 7: Knowledge base retrieval**
*For any* disease information request, the AI response should contain content from the Medical Knowledge Base
**Validates: Requirements 2.3**

**Property 8: Conversation persistence**
*For any* conversation between user and AI, all messages should be retrievable from conversation history
**Validates: Requirements 2.4**

**Property 9: AI response compliance**
*For any* AI-generated health information, treatment guidance, or symptom analysis, the response must include appropriate disclaimers, confidence scores, and consultation warnings
**Validates: Requirements 2.5, 8.1, 8.2, 8.3**

**Property 10: Symptom autocomplete accuracy**
*For any* partial symptom string, autocomplete suggestions should only include symptoms from the validated symptom database
**Validates: Requirements 3.1**

**Property 11: Prediction confidence threshold**
*For any* symptom analysis, all returned disease predictions should have confidence scores >= 0.6
**Validates: Requirements 3.2**

**Property 12: Risk severity assignment**
*For any* completed symptom analysis, a risk severity level (low, medium, high, critical) must be assigned
**Validates: Requirements 3.3**

**Property 13: Top predictions limit**
*For any* symptom analysis with results, exactly the top 3 most likely diseases should be returned with confidence scores
**Validates: Requirements 3.4**

**Property 14: High-risk consultation recommendation**
*For any* symptom analysis with high or critical risk severity, the recommendations must include immediate medical consultation
**Validates: Requirements 3.5**

**Property 15: File upload validation**
*For any* uploaded file, files exceeding 10MB or with invalid formats (not PDF/image) should be rejected with validation error
**Validates: Requirements 4.1**

**Property 16: OCR extraction accuracy**
*For any* valid lab report with known ground truth, OCR extraction accuracy should exceed 90%
**Validates: Requirements 4.2**

**Property 17: Lab value comparison**
*For any* extracted lab values, each value should be compared against medical standard ranges and flagged if abnormal
**Validates: Requirements 4.3, 4.4**

**Property 18: Lab analysis completeness**
*For any* completed lab report analysis, the results must include preventive suggestions and dietary recommendations
**Validates: Requirements 4.5**

**Property 19: Medication data round-trip**
*For any* medication details entered by a user, storing then retrieving should return the same name, dosage, and schedule
**Validates: Requirements 5.1**

**Property 20: Scheduled medication reminders**
*For any* medication with scheduled time, a notification should be delivered at the scheduled time (within 1-minute tolerance)
**Validates: Requirements 5.2**

**Property 21: Adherence tracking update**
*For any* medication adherence confirmation, an adherence record should be created and the adherence score should be recalculated
**Validates: Requirements 5.3**

**Property 22: Active medication display**
*For any* user viewing their medication dashboard, all active medications with dosage instructions should be displayed
**Validates: Requirements 5.4**

**Property 23: Missed dose alert threshold**
*For any* medication with 3 consecutive missed doses, a health warning alert should be sent to the user
**Validates: Requirements 5.5**

**Property 24: Appointment persistence and scheduling**
*For any* created appointment, the appointment details should be stored and a reminder notification should be scheduled
**Validates: Requirements 6.1**

**Property 25: Appointment reminder timing**
*For any* appointment within 24 hours, a reminder notification should be sent to the user
**Validates: Requirements 6.2**

**Property 26: Treatment progress update**
*For any* completed treatment milestone, the progress tracking should reflect the completion
**Validates: Requirements 6.3**

**Property 27: Follow-up reminder creation**
*For any* treatment plan requiring follow-up, a follow-up reminder should be automatically created based on the timeline
**Validates: Requirements 6.4**

**Property 28: Care timeline completeness**
*For any* user viewing their care timeline, all past and upcoming appointments with progress indicators should be displayed
**Validates: Requirements 6.5**

**Property 29: Sensitive data encryption**
*For any* sensitive patient data stored in the database, the data should be encrypted using AES-256
**Validates: Requirements 7.1**

**Property 30: Authorization verification**
*For any* attempt to access protected resources, the system should verify JWT token validity and role-based permissions
**Validates: Requirements 7.3**

**Property 31: Audit trail logging**
*For any* data access operation, an audit log entry should be created with user, action, resource, and timestamp
**Validates: Requirements 7.4**

**Property 32: Account lockout threshold**
*For any* account with 5 consecutive failed authentication attempts, the account should be temporarily locked and a security alert sent
**Validates: Requirements 7.5**

**Property 33: Sensitive topic consultation recommendation**
*For any* conversation involving predefined sensitive health topics, the AI should recommend professional medical consultation
**Validates: Requirements 8.4**

**Property 34: Training data anonymization**
*For any* data used for model training, the dataset should not contain real patient identifiers (verified by pattern matching)
**Validates: Requirements 8.5**

**Property 35: Concurrent user performance**
*For any* API request under load of 1000 concurrent users, response time should remain below 2 seconds
**Validates: Requirements 9.1**

**Property 36: Cache effectiveness**
*For any* frequently accessed medical knowledge, the second request should be served faster than the first (cache hit)
**Validates: Requirements 9.2**

**Property 37: API response format**
*For any* API endpoint call, the response should be valid JSON with appropriate HTTP status code (2xx, 4xx, 5xx)
**Validates: Requirements 10.1**

**Property 38: Validation error detail**
*For any* API request with validation errors, the error response should include field-level error messages
**Validates: Requirements 10.2**

**Property 39: Error logging and handling**
*For any* unexpected error, the error should be logged with stack trace and a generic error message returned to client
**Validates: Requirements 10.3**

**Property 40: Rate limit enforcement**
*For any* API request exceeding rate limits, the response should be HTTP 429 with retry-after header
**Validates: Requirements 10.5**

**Property 41: Offline mode handling**
*For any* network connectivity loss, offline indicators should be displayed and user actions should be queued for retry
**Validates: Requirements 12.4**

**Property 42: Data backward compatibility**
*For any* application update, user data from previous versions should remain accessible and functional
**Validates: Requirements 12.5**

## Error Handling

### Error Categories

**1. Validation Errors (HTTP 400)**
- Invalid input format
- Missing required fields
- Data type mismatches
- Constraint violations

**Response Format:**
```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

**2. Authentication Errors (HTTP 401)**
- Invalid credentials
- Expired tokens
- Missing authentication

**Response Format:**
```json
{
  "error": "authentication_error",
  "message": "Invalid or expired token"
}
```

**3. Authorization Errors (HTTP 403)**
- Insufficient permissions
- Resource access denied

**Response Format:**
```json
{
  "error": "authorization_error",
  "message": "You do not have permission to access this resource"
}
```

**4. Not Found Errors (HTTP 404)**
- Resource does not exist
- Invalid endpoint

**Response Format:**
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

**5. Rate Limit Errors (HTTP 429)**
- Too many requests
- Quota exceeded

**Response Format:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "retry_after": 60
}
```

**6. Server Errors (HTTP 500)**
- Unexpected exceptions
- Database connection failures
- External service failures

**Response Format:**
```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred",
  "request_id": "uuid"
}
```

### Error Handling Strategy

**Frontend:**
- Display user-friendly error messages
- Implement retry logic with exponential backoff
- Cache failed requests for offline mode
- Log errors to monitoring service
- Provide fallback UI states

**Backend:**
- Catch all exceptions at middleware level
- Log errors with context (user, request, stack trace)
- Return appropriate HTTP status codes
- Never expose sensitive information in error messages
- Implement circuit breakers for external services

**AI Services:**
- Handle API rate limits gracefully
- Implement fallback responses for AI failures
- Validate AI outputs before returning to users
- Log prediction failures for model improvement
- Set timeouts for long-running operations

## Testing Strategy

### Unit Testing

**Framework:** pytest for Python backend, Flutter test for frontend

**Coverage Requirements:**
- Minimum 80% code coverage
- All business logic functions tested
- Edge cases and boundary conditions covered

**Key Areas:**
- Data validation functions
- Authentication and authorization logic
- Database query functions
- API endpoint handlers
- Data transformation utilities

**Example Unit Tests:**
- Test user registration with valid data
- Test login with invalid credentials
- Test medication schedule calculation
- Test lab value comparison logic
- Test risk severity calculation

### Property-Based Testing

**Framework:** Hypothesis for Python backend

**Configuration:**
- Minimum 100 iterations per property test
- Use custom generators for domain-specific data
- Shrink failing examples for debugging

**Property Test Requirements:**
- Each correctness property MUST be implemented as a property-based test
- Each test MUST be tagged with: `**Feature: ai-patient-support-assistant, Property {number}: {property_text}**`
- Each property MUST reference the requirement it validates

**Key Property Tests:**
1. User data round-trip (Property 1)
2. Authentication token generation (Property 2)
3. Session expiration enforcement (Property 3)
4. User data isolation (Property 4)
5. AI response time constraint (Property 5)
6. Conversation persistence (Property 8)
7. AI response compliance (Property 9)
8. Symptom autocomplete accuracy (Property 10)
9. Prediction confidence threshold (Property 11)
10. Risk severity assignment (Property 12)
11. File upload validation (Property 15)
12. Lab value comparison (Property 17)
13. Medication data round-trip (Property 19)
14. Adherence tracking update (Property 21)
15. Appointment persistence (Property 24)
16. Sensitive data encryption (Property 29)
17. Authorization verification (Property 30)
18. Audit trail logging (Property 31)
19. API response format (Property 37)
20. Validation error detail (Property 38)

**Example Property Test Structure:**
```python
from hypothesis import given, strategies as st
import pytest

# **Feature: ai-patient-support-assistant, Property 1: User data round-trip consistency**
@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=50),
    first_name=st.text(min_size=1, max_size=50),
    last_name=st.text(min_size=1, max_size=50)
)
def test_user_registration_round_trip(email, password, first_name, last_name):
    """For any valid user registration data, storing then retrieving should return equivalent values"""
    # Register user
    user_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    }
    user_id = auth_service.register_user(**user_data)
    
    # Retrieve user
    retrieved_user = auth_service.get_user(user_id)
    
    # Assert equivalence (password should be hashed, not plain)
    assert retrieved_user.email == email
    assert retrieved_user.first_name == first_name
    assert retrieved_user.last_name == last_name
    assert retrieved_user.password_hash != password  # Should be encrypted
```

### Integration Testing

**Framework:** pytest with test database

**Key Integration Tests:**
- End-to-end user registration and login flow
- Complete symptom analysis workflow
- Lab report upload and analysis pipeline
- Medication reminder scheduling and delivery
- Appointment creation and notification flow

**Test Environment:**
- Isolated test databases (PostgreSQL, MongoDB)
- Mocked external services (OpenAI, AWS Textract, FCM)
- Test data fixtures for consistent testing

### Performance Testing

**Framework:** Locust or Apache JMeter

**Test Scenarios:**
- 1000 concurrent users accessing API endpoints
- AI response time under load
- Database query performance
- Cache hit rates
- Autoscaling trigger points

**Performance Targets:**
- API response time: < 2 seconds (95th percentile)
- AI chat response: < 3 seconds
- Database queries: < 100ms
- File upload: < 5 seconds for 10MB files

### Security Testing

**Areas to Test:**
- SQL injection prevention
- XSS attack prevention
- CSRF protection
- JWT token security
- Data encryption verification
- Rate limiting effectiveness
- Account lockout mechanism

**Tools:**
- OWASP ZAP for vulnerability scanning
- Bandit for Python security linting
- Manual penetration testing

## Deployment Architecture

### Containerization

**Docker Images:**
1. `patient-support-auth-api`: Authentication service
2. `patient-support-core-api`: Core business logic API
3. `patient-support-ai-service`: AI processing service
4. `patient-support-notification-service`: Notification handler

**Base Image:** python:3.11-slim

**Dockerfile Example:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:create_app()"]
```

### AWS Infrastructure

**Compute:**
- AWS ECS Fargate for containerized services
- AWS EC2 P3 instances for GPU-accelerated AI inference
- Auto Scaling Groups for horizontal scaling

**Storage:**
- AWS RDS PostgreSQL (Multi-AZ deployment)
- AWS DocumentDB (MongoDB-compatible)
- AWS S3 for lab report storage
- AWS ElastiCache Redis for caching

**Networking:**
- AWS VPC with public and private subnets
- Application Load Balancer for traffic distribution
- AWS CloudFront for CDN (optional)
- AWS Route 53 for DNS management

**Security:**
- AWS Secrets Manager for credentials
- AWS KMS for encryption keys
- AWS WAF for web application firewall
- AWS Shield for DDoS protection

**Monitoring:**
- AWS CloudWatch for logs and metrics
- AWS X-Ray for distributed tracing
- Custom dashboards for health monitoring
- Alerts for critical errors and performance degradation

### CI/CD Pipeline

**Pipeline Stages:**
1. **Source:** GitHub repository
2. **Build:** Docker image creation
3. **Test:** Automated test execution
4. **Security Scan:** Container vulnerability scanning
5. **Deploy to Staging:** Automated deployment
6. **Integration Tests:** End-to-end testing
7. **Manual Approval:** Production deployment gate
8. **Deploy to Production:** Blue-green deployment
9. **Health Checks:** Automated verification
10. **Rollback:** Automatic rollback on failure

**Tools:**
- GitHub Actions or AWS CodePipeline
- AWS CodeBuild for building
- AWS ECR for container registry
- Terraform for infrastructure as code

### Scaling Strategy

**Horizontal Scaling:**
- API services: Scale based on CPU utilization (> 70%)
- AI services: Scale based on request queue depth
- Target: 2-10 instances per service

**Vertical Scaling:**
- Database: Upgrade instance types during maintenance windows
- Redis: Increase memory allocation as needed

**Caching Strategy:**
- Cache medical knowledge base queries (TTL: 24 hours)
- Cache user sessions (TTL: 1 hour)
- Cache symptom autocomplete results (TTL: 1 week)

### High Availability

**Database:**
- Multi-AZ deployment for automatic failover
- Read replicas for read-heavy operations
- Automated backups with point-in-time recovery

**Application:**
- Multiple availability zones
- Health checks with automatic instance replacement
- Circuit breakers for external service failures

**Disaster Recovery:**
- Regular database backups to S3
- Cross-region replication for critical data
- Documented recovery procedures
- RTO: 4 hours, RPO: 1 hour

## Security Implementation

### Authentication Flow

1. User submits credentials
2. Backend validates credentials
3. Generate JWT access token (15 min expiry) and refresh token (7 days expiry)
4. Return tokens to client
5. Client stores tokens securely (encrypted storage)
6. Client includes access token in Authorization header
7. Backend validates token on each request
8. Client refreshes access token using refresh token when expired

### Data Encryption

**At Rest:**
- Database: AWS RDS encryption with KMS
- Files: S3 server-side encryption (SSE-KMS)
- Application-level: AES-256 for sensitive fields

**In Transit:**
- TLS 1.3 for all client-server communication
- Certificate management via AWS Certificate Manager
- HTTPS enforcement with HSTS headers

### Access Control

**Role-Based Access Control (RBAC):**
- Roles: patient, admin, healthcare_provider
- Permissions: read, write, delete, admin
- Middleware validates user role before resource access

**Data Access Policies:**
- Users can only access their own data
- Admins can access aggregated anonymized data
- Healthcare providers require explicit patient consent

### Compliance Considerations

**HIPAA Alignment:**
- Encrypted data storage and transmission
- Audit logging of all data access
- Access controls and authentication
- Data backup and disaster recovery
- Business Associate Agreements (BAAs) with vendors

**GDPR Considerations:**
- User consent for data processing
- Right to data access and deletion
- Data portability
- Privacy by design principles

**Medical Disclaimers:**
- Clear statements that AI provides guidance, not diagnosis
- Recommendations to consult healthcare professionals
- Transparency about AI limitations and confidence levels

## API Documentation

### Authentication Endpoints

**POST /api/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male"
}

Response (201):
{
  "user_id": "uuid",
  "email": "user@example.com",
  "message": "Registration successful"
}
```

**POST /api/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John"
  }
}
```

### Chat Endpoints

**POST /api/chat/message**
```json
Request:
{
  "message": "What is diabetes?",
  "conversation_id": "uuid"
}

Response (200):
{
  "message_id": "uuid",
  "response": "Diabetes is a condition where your body has trouble managing blood sugar levels...",
  "disclaimer": "This information is for guidance only. Please consult a healthcare professional.",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

### Symptom Analysis Endpoints

**POST /api/symptoms/analyze**
```json
Request:
{
  "symptoms": ["fever", "cough", "fatigue"]
}

Response (200):
{
  "analysis_id": "uuid",
  "risk_severity": "medium",
  "possible_conditions": [
    {
      "disease": "Common Cold",
      "confidence": 0.75,
      "description": "A viral infection of the upper respiratory tract"
    },
    {
      "disease": "Influenza",
      "confidence": 0.68,
      "description": "A contagious respiratory illness caused by influenza viruses"
    },
    {
      "disease": "COVID-19",
      "confidence": 0.62,
      "description": "An infectious disease caused by the SARS-CoV-2 virus"
    }
  ],
  "recommended_action": "Monitor symptoms and consult a healthcare provider if they worsen",
  "disclaimer": "This is not a medical diagnosis. Please consult a healthcare professional."
}
```

### Lab Report Endpoints

**POST /api/lab-reports/upload**
```
Content-Type: multipart/form-data

file: [binary data]

Response (202):
{
  "report_id": "uuid",
  "status": "processing",
  "message": "Lab report uploaded successfully and is being processed"
}
```

**GET /api/lab-reports/{report_id}/analysis**
```json
Response (200):
{
  "report_id": "uuid",
  "report_date": "2026-02-01",
  "results": [
    {
      "test_name": "Glucose",
      "value": 110,
      "unit": "mg/dL",
      "reference_range": "70-100",
      "status": "high",
      "interpretation": "Your blood sugar is slightly elevated",
      "recommendations": ["Monitor carbohydrate intake", "Increase physical activity"]
    }
  ],
  "overall_summary": "Most values are within normal range with slight elevation in glucose",
  "preventive_suggestions": ["Maintain a balanced diet", "Regular exercise", "Stay hydrated"]
}
```

### Medication Endpoints

**POST /api/medications**
```json
Request:
{
  "name": "Metformin",
  "dosage": "500mg",
  "frequency": "twice_daily",
  "schedule_times": ["08:00", "20:00"],
  "start_date": "2026-02-07",
  "instructions": "Take with meals"
}

Response (201):
{
  "medication_id": "uuid",
  "name": "Metformin",
  "message": "Medication added successfully",
  "next_reminder": "2026-02-07T08:00:00Z"
}
```

## Mobile App Architecture

### State Management

**Pattern:** Provider/Riverpod

**State Categories:**
- Authentication state (user session, tokens)
- UI state (loading, errors, form inputs)
- Data state (medications, appointments, conversations)
- Cache state (offline data)

### Navigation

**Pattern:** Named routes with Navigator 2.0

**Route Structure:**
```
/login
/register
/home
/chat
/chat/:conversationId
/symptoms
/symptoms/results/:analysisId
/lab-reports
/lab-reports/upload
/lab-reports/:reportId
/medications
/medications/add
/appointments
/appointments/add
/profile
```

### Offline Support

**Strategy:**
- Cache API responses locally
- Queue write operations when offline
- Sync when connection restored
- Display offline indicators

**Implementation:**
- SQLite for local data storage
- Shared Preferences for settings
- Queue manager for pending operations

### Push Notifications

**Firebase Cloud Messaging Integration:**
- Register device token on app launch
- Handle foreground notifications
- Handle background notifications
- Navigate to relevant screen on tap

**Notification Types:**
- Medication reminders
- Appointment reminders
- Health warnings
- Follow-up reminders

## Monitoring and Observability

### Metrics to Track

**Application Metrics:**
- Request rate (requests/second)
- Error rate (errors/total requests)
- Response time (p50, p95, p99)
- Active users
- API endpoint usage

**Business Metrics:**
- User registrations
- Chat conversations initiated
- Symptom analyses performed
- Lab reports uploaded
- Medication adherence rate
- Appointment completion rate

**Infrastructure Metrics:**
- CPU utilization
- Memory usage
- Disk I/O
- Network throughput
- Database connections
- Cache hit rate

### Logging Strategy

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages for potential issues
- ERROR: Error messages for failures
- CRITICAL: Critical issues requiring immediate attention

**Structured Logging:**
```json
{
  "timestamp": "2026-02-07T10:30:00Z",
  "level": "INFO",
  "service": "core-api",
  "user_id": "uuid",
  "request_id": "uuid",
  "message": "User profile updated",
  "metadata": {
    "fields_updated": ["first_name", "phone_number"]
  }
}
```

### Alerting

**Critical Alerts:**
- Service downtime
- Error rate > 5%
- Response time > 5 seconds
- Database connection failures
- AI service failures

**Warning Alerts:**
- Error rate > 2%
- Response time > 2 seconds
- CPU utilization > 80%
- Memory usage > 85%
- Disk space < 20%

**Alert Channels:**
- Email for non-critical alerts
- SMS for critical alerts
- Slack/Teams integration
- PagerDuty for on-call rotation

## Future Enhancements

1. **Voice Interaction:** Full voice-based chat interface
2. **Wearable Integration:** Sync with fitness trackers and smartwatches
3. **Telemedicine:** Video consultation integration
4. **Multi-language Support:** Internationalization for global reach
5. **Advanced Analytics:** Predictive health insights and trends
6. **Family Accounts:** Manage health for family members
7. **Insurance Integration:** Claims and coverage information
8. **Pharmacy Integration:** Direct prescription fulfillment
9. **Health Records Import:** Integration with EHR systems
10. **AI Model Improvements:** Continuous learning from user interactions
