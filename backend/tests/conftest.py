"""Pytest configuration and fixtures"""
import pytest
import os
import sys

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/patient_support_test'


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Any global test setup can go here
    yield
    # Cleanup after all tests
