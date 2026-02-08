# Contributing to AI Patient Support Assistant

Thank you for your interest in contributing to the AI Patient Support Assistant! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check if the feature has been suggested in Issues
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards below
   - Write tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   pytest
   pytest --cov=app
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Provide clear description
   - Reference related issues
   - Ensure CI passes

## Development Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL, MongoDB, Redis

### Setup Steps

1. Clone your fork
   ```bash
   git clone https://github.com/your-username/ai-patient-support-assistant.git
   cd ai-patient-support-assistant
   ```

2. Create virtual environment
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start services
   ```bash
   docker-compose up -d
   ```

6. Run migrations
   ```bash
   python migrations/run_migrations.py
   python -m app.mongodb.init_collections
   python -m app.mongodb.seed_data
   ```

## Coding Standards

### Python Code Style

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names

**Example:**
```python
def calculate_risk_severity(predictions: List[Dict]) -> str:
    """
    Calculate risk severity from predictions
    
    Args:
        predictions: List of prediction dicts with confidence scores
    
    Returns:
        Risk level: 'low', 'medium', 'high', or 'critical'
    """
    if not predictions:
        return 'low'
    
    max_confidence = max(p['confidence'] for p in predictions)
    
    if max_confidence >= 0.9:
        return 'high'
    elif max_confidence >= 0.75:
        return 'medium'
    else:
        return 'low'
```

### Documentation

- Add docstrings to all functions and classes
- Update README.md for new features
- Add inline comments for complex logic
- Update API documentation

### Testing

- Write property-based tests using Hypothesis
- Aim for 100+ iterations per property test
- Test edge cases and error conditions
- Maintain test coverage above 80%

**Example Property Test:**
```python
from hypothesis import given, strategies as st, settings

@given(
    symptoms=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10)
)
@settings(max_examples=100)
def test_symptom_analysis_returns_valid_predictions(symptoms):
    """Test that symptom analysis always returns valid predictions"""
    service = SymptomAnalysisService()
    result = service.analyze_symptoms(symptoms)
    
    assert 'predictions' in result
    assert len(result['predictions']) <= 3
    
    for pred in result['predictions']:
        assert 'disease' in pred
        assert 'confidence' in pred
        assert 0 <= pred['confidence'] <= 1.0
```

### Commit Messages

Use clear, descriptive commit messages:

```
Add feature: symptom search autocomplete

- Implement MongoDB text search
- Add query parameter validation
- Include unit tests
- Update API documentation

Closes #123
```

Format:
- First line: Brief summary (50 chars max)
- Blank line
- Detailed description (if needed)
- Reference issues

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy & MongoDB models
│   ├── routes/          # API endpoints (Flask blueprints)
│   ├── services/        # Business logic
│   ├── middleware/      # JWT auth, audit logging
│   ├── mongodb/         # MongoDB collections
│   └── utils/           # Helper functions
├── migrations/          # Database migrations
├── tests/
│   ├── conftest.py     # Test fixtures
│   └── test_properties/ # Property-based tests
└── requirements.txt     # Dependencies
```

## Testing Guidelines

### Unit Tests
- Test individual functions
- Mock external dependencies
- Test error conditions

### Property-Based Tests
- Test universal properties
- Use Hypothesis for random data generation
- Run 100+ iterations

### Integration Tests
- Test API endpoints
- Test database interactions
- Test service integrations

## Security Guidelines

- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Encrypt sensitive data at rest
- Validate all user inputs
- Follow OWASP security practices

## Documentation

### Code Documentation
- Docstrings for all public functions
- Type hints for function parameters
- Inline comments for complex logic

### API Documentation
- Document all endpoints
- Include request/response examples
- Specify authentication requirements
- Document error responses

## Review Process

1. **Automated Checks**
   - Tests must pass
   - Code style checks
   - Security scans

2. **Code Review**
   - At least one approval required
   - Address reviewer feedback
   - Maintain code quality

3. **Merge**
   - Squash commits if needed
   - Update changelog
   - Close related issues

## Questions?

- Open an issue for questions
- Join our community discussions
- Email: support@example.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to better healthcare accessibility! 🙏
