# API Documentation

Complete API reference for the AI Patient Support Assistant.

## Base URL

```
Development: http://localhost:5000
Production: https://api.yourdomain.com
```

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Response Format

All responses follow this format:

**Success Response:**
```json
{
  "data": { ... },
  "message": "Success message"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "details": { ... }
}
```

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone_number": "+12025551234",
  "address": "123 Main St",
  "emergency_contact": "+12025555678"
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user_id": "uuid-here"
}
```

**Errors:**
- `400` - Invalid email format
- `400` - Password too weak
- `409` - Email already exists

---

### Login

Authenticate and receive JWT tokens.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Errors:**
- `401` - Invalid credentials
- `403` - Account locked (too many failed attempts)

---

### Refresh Token

Get a new access token using refresh token.

**Endpoint:** `POST /api/auth/refresh`

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Get Profile

Retrieve current user's profile.

**Endpoint:** `GET /api/auth/profile`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone_number": "+12025551234",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Update Profile

Update user profile information.

**Endpoint:** `PUT /api/auth/profile`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+12025551234",
  "address": "456 New St"
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully"
}
```

---

## Chat Endpoints

### Send Message

Send a message to the AI assistant.

**Endpoint:** `POST /api/chat/message`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "message": "What are the symptoms of diabetes?",
  "conversation_id": "optional-uuid"
}
```

**Response:** `200 OK`
```json
{
  "response": "Diabetes symptoms include increased thirst, frequent urination...",
  "conversation_id": "uuid",
  "response_time": 1.234,
  "tokens_used": 150,
  "readability": {
    "score": 65.5,
    "level": "standard (8th-9th grade)",
    "is_easy": true
  }
}
```

**Emergency Response:**
```json
{
  "response": "🚨 EMERGENCY ALERT 🚨\n\nBased on your message...",
  "conversation_id": "uuid",
  "emergency": true,
  "response_time": 0.5
}
```

---

### Get Conversation History

Retrieve messages from a conversation.

**Endpoint:** `GET /api/chat/history/{conversation_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "conversation_id": "uuid",
  "title": "Conversation about diabetes",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T01:00:00Z",
  "message_count": 10,
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "What are the symptoms of diabetes?",
      "created_at": "2024-01-01T00:00:00Z",
      "metadata": {}
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Diabetes symptoms include...",
      "created_at": "2024-01-01T00:00:01Z",
      "metadata": {
        "tokens_used": 150,
        "model": "gpt-4"
      }
    }
  ]
}
```

---

### List Conversations

Get all conversations for the current user.

**Endpoint:** `GET /api/chat/conversations`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (optional): Max results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Conversation about diabetes",
      "message_count": 10,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T01:00:00Z",
      "last_message": "Diabetes symptoms include...",
      "last_message_time": "2024-01-01T01:00:00Z"
    }
  ],
  "count": 1,
  "limit": 20,
  "offset": 0
}
```

---

### Delete Conversation

Delete a conversation and all its messages.

**Endpoint:** `DELETE /api/chat/conversations/{conversation_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "message": "Conversation deleted successfully"
}
```

---

## Symptom Analysis Endpoints

### Search Symptoms

Search for symptoms with autocomplete.

**Endpoint:** `GET /api/symptoms/search`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `q` (required): Search query (min 2 characters)
- `limit` (optional): Max results (default: 10, max: 50)

**Example:** `GET /api/symptoms/search?q=fever&limit=5`

**Response:** `200 OK`
```json
{
  "query": "fever",
  "results": [
    {
      "name": "Fever",
      "description": "Elevated body temperature above normal",
      "severity": "medium",
      "common_diseases": ["Common Cold", "Flu", "COVID-19"]
    }
  ],
  "count": 1
}
```

---

### Analyze Symptoms

Analyze symptoms and get disease predictions.

**Endpoint:** `POST /api/symptoms/analyze`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "symptoms": ["fever", "cough", "headache"],
  "age": 30,
  "gender": "male"
}
```

**Response:** `200 OK`
```json
{
  "analysis_id": "uuid",
  "symptoms": ["fever", "cough", "headache"],
  "risk_severity": "medium",
  "predictions": [
    {
      "disease": "Common Cold",
      "confidence": 0.85,
      "description": "A viral infection of the upper respiratory tract",
      "treatment_options": [
        "Rest and hydration",
        "Over-the-counter pain relievers",
        "Decongestants"
      ],
      "when_to_see_doctor": "If symptoms persist for more than 10 days"
    },
    {
      "disease": "Flu",
      "confidence": 0.72,
      "description": "Influenza viral infection",
      "treatment_options": [
        "Antiviral medications",
        "Rest",
        "Fluids"
      ],
      "when_to_see_doctor": "If symptoms are severe or you're in a high-risk group"
    }
  ],
  "recommendations": [
    "📋 Consider scheduling a doctor's appointment within the next few days",
    "Keep track of your symptoms and any changes",
    "Rest and stay hydrated",
    "Keep a symptom diary to share with your healthcare provider"
  ],
  "disclaimer": "⚕️ **Important Medical Disclaimer**: This analysis is for informational purposes only..."
}
```

**Risk Severity Levels:**
- `low` - Monitor symptoms
- `medium` - Consider doctor visit
- `high` - See doctor soon
- `critical` - Seek immediate medical attention

---

### Get Symptom Analysis History

Retrieve past symptom analyses.

**Endpoint:** `GET /api/symptoms/history`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (optional): Max results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "analyses": [
    {
      "id": "uuid",
      "symptoms": ["fever", "cough"],
      "risk_level": "medium",
      "confidence_score": 0.78,
      "predictions": [...],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 1,
  "limit": 20,
  "offset": 0
}
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Default**: 100 requests per minute per user
- **Burst**: 200 requests per minute (short bursts allowed)

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**Rate Limit Exceeded Response:** `429 Too Many Requests`
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## Error Handling

### Common Error Responses

**Validation Error:** `400 Bad Request`
```json
{
  "error": "Validation failed",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

**Authentication Error:** `401 Unauthorized`
```json
{
  "error": "Authentication required",
  "message": "Please provide a valid access token"
}
```

**Authorization Error:** `403 Forbidden`
```json
{
  "error": "Insufficient permissions",
  "message": "You don't have access to this resource"
}
```

**Not Found:** `404 Not Found`
```json
{
  "error": "Resource not found",
  "message": "The requested resource does not exist"
}
```

**Server Error:** `500 Internal Server Error`
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Webhooks (Planned)

Future support for webhooks to notify external systems of events.

---

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'SecurePass123'
})
tokens = response.json()

# Send chat message
headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
response = requests.post('http://localhost:5000/api/chat/message',
    headers=headers,
    json={'message': 'What are the symptoms of diabetes?'}
)
print(response.json())
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123'
  })
});
const tokens = await loginResponse.json();

// Send chat message
const chatResponse = await fetch('http://localhost:5000/api/chat/message', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${tokens.access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'What are the symptoms of diabetes?'
  })
});
const result = await chatResponse.json();
console.log(result);
```

---

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Authentication & authorization
- AI chat assistant
- Symptom analysis
- Security features

---

## Support

For API support:
- GitHub Issues: https://github.com/yourusername/ai-patient-support-assistant/issues
- Email: api-support@example.com
- Documentation: https://docs.example.com

---

**Last Updated:** 2024
**API Version:** 1.0
