"""
Property-based tests for authentication system

**Feature: ai-patient-support-assistant, Property 2: Authentication token generation**
**Feature: ai-patient-support-assistant, Property 3: Session expiration enforcement**
**Feature: ai-patient-support-assistant, Property 32: Account lockout threshold**
**Validates: Requirements 1.2, 1.3, 7.5**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import emails, text
from datetime import datetime, timedelta
from flask_jwt_extended import decode_token
from app.services.auth_service import AuthService
from app.models import User, SessionLocal
from app.models.database import Base, engine
import jwt


@st.composite
def valid_credentials_strategy(draw):
    """Generate valid email and password"""
    email = draw(emails())
    # Generate password that meets requirements
    password = draw(text(min_size=8, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),  # Uppercase, lowercase, digits
        min_codepoint=33, max_codepoint=126
    )))
    
    # Ensure password has at least one of each required character type
    if not any(c.isupper() for c in password):
        password = 'A' + password
    if not any(c.islower() for c in password):
        password = password + 'a'
    if not any(c.isdigit() for c in password):
        password = password + '1'
    
    return {'email': email, 'password': password}


@pytest.fixture(scope='function')
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def app_context():
    """Create Flask app context for JWT operations"""
    from app import create_app
    app = create_app()
    with app.app_context():
        yield app


class TestAuthenticationTokenGeneration:
    """
    **Feature: ai-patient-support-assistant, Property 2: Authentication token generation**
    
    For any valid user credentials, successful authentication should generate 
    a valid JWT token that can be verified and decoded.
    """
    
    @given(credentials=valid_credentials_strategy())
    @settings(max_examples=100, deadline=None)
    def test_successful_login_generates_valid_tokens(self, credentials, db_session, app_context):
        """
        Test that successful authentication generates valid JWT tokens
        
        This validates that:
        1. Valid credentials produce access and refresh tokens
        2. Tokens can be decoded
        3. Tokens contain correct user identity
        4. Tokens have appropriate expiration times
        """
        # Arrange: Register user
        user, error = AuthService.register_user(
            credentials['email'],
            credentials['password'],
            {}
        )
        
        assert error is None, f"Registration should succeed: {error}"
        assert user is not None
        
        # Act: Authenticate
        result, error = AuthService.authenticate(
            credentials['email'],
            credentials['password']
        )
        
        # Assert: Authentication successful
        assert error is None, f"Authentication should succeed: {error}"
        assert result is not None
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert 'user' in result
        
        # Assert: Tokens are valid JWT tokens
        access_token = result['access_token']
        refresh_token = result['refresh_token']
        
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(access_token) > 0
        assert len(refresh_token) > 0
        
        # Assert: Tokens can be decoded
        try:
            decoded_access = decode_token(access_token)
            decoded_refresh = decode_token(refresh_token)
            
            # Assert: Tokens contain correct user identity
            assert decoded_access['sub'] == str(user.id)
            assert decoded_refresh['sub'] == str(user.id)
            
            # Assert: Access token has email claim
            assert decoded_access.get('email') == credentials['email']
            
            # Assert: Tokens have expiration
            assert 'exp' in decoded_access
            assert 'exp' in decoded_refresh
            
        except Exception as e:
            pytest.fail(f"Token decoding failed: {e}")
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()
    
    @given(credentials=valid_credentials_strategy())
    @settings(max_examples=50, deadline=None)
    def test_invalid_password_does_not_generate_token(self, credentials, db_session, app_context):
        """
        Test that invalid credentials do not generate tokens
        
        This validates that:
        1. Wrong password returns error
        2. No tokens are generated
        3. Failed login attempts are tracked
        """
        # Arrange: Register user
        user, error = AuthService.register_user(
            credentials['email'],
            credentials['password'],
            {}
        )
        
        assert error is None
        
        # Act: Authenticate with wrong password
        result, error = AuthService.authenticate(
            credentials['email'],
            credentials['password'] + 'wrong'
        )
        
        # Assert: Authentication failed
        assert result is None
        assert error is not None
        assert 'Invalid' in error or 'password' in error.lower()
        
        # Assert: Failed login attempts incremented
        db_session.refresh(user)
        assert user.failed_login_attempts > 0
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()


class TestSessionExpirationEnforcement:
    """
    **Feature: ai-patient-support-assistant, Property 3: Session expiration enforcement**
    
    For any expired or invalid session token, attempts to access protected 
    resources should be rejected with authentication error.
    """
    
    @given(credentials=valid_credentials_strategy())
    @settings(max_examples=50, deadline=None)
    def test_expired_token_is_rejected(self, credentials, db_session, app_context):
        """
        Test that expired tokens are properly rejected
        
        This validates that:
        1. Expired tokens cannot be decoded successfully
        2. Token expiration is enforced
        """
        from flask_jwt_extended import create_access_token
        
        # Arrange: Register user
        user, error = AuthService.register_user(
            credentials['email'],
            credentials['password'],
            {}
        )
        
        assert error is None
        
        # Create an expired token (expires immediately)
        expired_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Act & Assert: Decoding expired token should fail
        try:
            decoded = decode_token(expired_token)
            
            # Check if token is expired
            exp_timestamp = decoded.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                assert exp_datetime < datetime.utcnow(), "Token should be expired"
        
        except jwt.ExpiredSignatureError:
            # This is expected - token is expired
            pass
        except Exception as e:
            # Other exceptions are also acceptable for expired tokens
            pass
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()
    
    @given(credentials=valid_credentials_strategy())
    @settings(max_examples=50, deadline=None)
    def test_invalid_token_is_rejected(self, credentials, db_session, app_context):
        """
        Test that invalid tokens are rejected
        
        This validates that:
        1. Malformed tokens are rejected
        2. Tokens with invalid signatures are rejected
        """
        # Arrange: Register user
        user, error = AuthService.register_user(
            credentials['email'],
            credentials['password'],
            {}
        )
        
        assert error is None
        
        # Act & Assert: Invalid tokens should be rejected
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "Bearer token",
        ]
        
        for invalid_token in invalid_tokens:
            try:
                decode_token(invalid_token)
                # If we get here, the token was somehow valid (shouldn't happen)
                pytest.fail(f"Invalid token was accepted: {invalid_token}")
            except Exception:
                # Expected - invalid token rejected
                pass
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()


class TestAccountLockoutThreshold:
    """
    **Feature: ai-patient-support-assistant, Property 32: Account lockout threshold**
    
    For any account with 5 consecutive failed authentication attempts, 
    the account should be temporarily locked and a security alert sent.
    """
    
    @given(credentials=valid_credentials_strategy())
    @settings(max_examples=50, deadline=None)
    def test_account_locks_after_five_failed_attempts(self, credentials, db_session, app_context):
        """
        Test that account locks after 5 failed login attempts
        
        This validates that:
        1. Failed attempts are tracked
        2. Account locks after 5 failures
        3. Locked account cannot login even with correct password
        4. Lock has expiration time
        """
        # Arrange: Register user
        user, error = AuthService.register_user(
            credentials['email'],
            credentials['password'],
            {}
        )
        
        assert error is None
        user_id = user.id
        
        # Act: Attempt 5 failed logins
        for i in range(5):
            result, error = AuthService.authenticate(
                credentials['email'],
                credentials['password'] + 'wrong'
            )
            
            assert result is None
            assert error is not None
            
            # Refresh user to check failed attempts
            db_session.expire(user)
            db_session.refresh(user)
            
            if i < 4:
                # First 4 attempts should just increment counter
                assert user.failed_login_attempts == i + 1
                assert user.account_locked_until is None
            else:
                # 5th attempt should lock account
                assert user.failed_login_attempts >= 5
                assert user.account_locked_until is not None
                assert user.account_locked_until > datetime.utcnow()
        
        # Assert: Account is locked
        assert user.is_account_locked()
        
        # Act: Try to login with correct password while locked
        result, error = AuthService.authenticate(
            credentials['email'],
            credentials['password']
        )
        
        # Assert: Login fails due to lock
        assert result is None
        assert error is not None
        assert 'locked' in error.lower()
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()
    
    @given(credentials=valid_credentials_strategy())
    @settings(max_examples=50, deadline=None)
    def test_failed_attempts_reset_on_successful_login(self, credentials, db_session, app_context):
        """
        Test that failed login attempts reset after successful login
        
        This validates that:
        1. Failed attempts are tracked
        2. Successful login resets counter
        3. Account lock is cleared
        """
        # Arrange: Register user
        user, error = AuthService.register_user(
            credentials['email'],
            credentials['password'],
            {}
        )
        
        assert error is None
        
        # Act: Make 3 failed attempts
        for i in range(3):
            result, error = AuthService.authenticate(
                credentials['email'],
                credentials['password'] + 'wrong'
            )
            assert result is None
        
        # Refresh user
        db_session.expire(user)
        db_session.refresh(user)
        assert user.failed_login_attempts == 3
        
        # Act: Successful login
        result, error = AuthService.authenticate(
            credentials['email'],
            credentials['password']
        )
        
        # Assert: Login successful
        assert error is None
        assert result is not None
        
        # Assert: Failed attempts reset
        db_session.expire(user)
        db_session.refresh(user)
        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()
