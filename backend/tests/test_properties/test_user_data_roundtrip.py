"""
Property-based tests for user data round-trip consistency

**Feature: ai-patient-support-assistant, Property 1: User data round-trip consistency**
**Validates: Requirements 1.1, 1.4**

For any valid user registration data or profile update, storing the data then 
retrieving it should return equivalent values with encrypted sensitive fields.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import emails, text, dates, sampled_from
from datetime import date, datetime
from app.models import User, SessionLocal
from app.models.database import Base, engine
import bcrypt


# Custom strategies for user data
@st.composite
def user_profile_strategy(draw):
    """Generate valid user profile data"""
    email = draw(emails())
    password = draw(text(min_size=8, max_size=50, alphabet=st.characters(blacklist_characters='\x00')))
    first_name = draw(text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L',))))
    last_name = draw(text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L',))))
    
    # Generate date of birth (must be in the past and reasonable age)
    today = date.today()
    min_date = date(today.year - 120, 1, 1)  # Max 120 years old
    max_date = date(today.year - 13, 12, 31)  # Min 13 years old
    date_of_birth = draw(dates(min_value=min_date, max_value=max_date))
    
    gender = draw(sampled_from(['male', 'female', 'other', 'prefer_not_to_say']))
    
    # Phone number (simple format)
    phone_number = draw(st.one_of(
        st.none(),
        st.text(min_size=10, max_size=15, alphabet='0123456789+-() ')
    ))
    
    return {
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'date_of_birth': date_of_birth,
        'gender': gender,
        'phone_number': phone_number
    }


@pytest.fixture(scope='function')
def db_session():
    """Create a test database session"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestUserDataRoundTrip:
    """Property-based tests for user data persistence"""
    
    @given(user_data=user_profile_strategy())
    @settings(max_examples=100, deadline=None)
    def test_user_registration_round_trip(self, user_data, db_session):
        """
        **Feature: ai-patient-support-assistant, Property 1: User data round-trip consistency**
        
        For any valid user registration data, storing the data then retrieving it 
        should return equivalent values with encrypted sensitive fields.
        
        This tests that:
        1. User data can be stored in the database
        2. Retrieved data matches stored data
        3. Password is encrypted (not stored in plain text)
        4. All fields are preserved correctly
        """
        # Arrange: Hash password
        password_plain = user_data['password']
        password_hash = bcrypt.hashpw(password_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Act: Create and store user
        user = User(
            email=user_data['email'],
            password_hash=password_hash,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            date_of_birth=user_data['date_of_birth'],
            gender=user_data['gender'],
            phone_number=user_data['phone_number']
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        user_id = user.id
        
        # Clear session to ensure we're reading from database
        db_session.expunge_all()
        
        # Act: Retrieve user
        retrieved_user = db_session.query(User).filter(User.id == user_id).first()
        
        # Assert: Data matches
        assert retrieved_user is not None, "User should be retrievable from database"
        assert retrieved_user.email == user_data['email'], "Email should match"
        assert retrieved_user.first_name == user_data['first_name'], "First name should match"
        assert retrieved_user.last_name == user_data['last_name'], "Last name should match"
        assert retrieved_user.date_of_birth == user_data['date_of_birth'], "Date of birth should match"
        assert retrieved_user.gender == user_data['gender'], "Gender should match"
        assert retrieved_user.phone_number == user_data['phone_number'], "Phone number should match"
        
        # Assert: Password is encrypted
        assert retrieved_user.password_hash != password_plain, "Password should be encrypted, not plain text"
        assert bcrypt.checkpw(password_plain.encode('utf-8'), retrieved_user.password_hash.encode('utf-8')), \
            "Encrypted password should be verifiable"
        
        # Assert: System fields are set
        assert retrieved_user.id is not None, "ID should be generated"
        assert retrieved_user.created_at is not None, "Created timestamp should be set"
        assert retrieved_user.is_active is True, "User should be active by default"
        
        # Cleanup
        db_session.delete(retrieved_user)
        db_session.commit()
    
    @given(
        original_data=user_profile_strategy(),
        update_data=st.fixed_dictionaries({
            'first_name': st.one_of(st.none(), text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L',)))),
            'last_name': st.one_of(st.none(), text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L',)))),
            'phone_number': st.one_of(st.none(), text(min_size=10, max_size=15, alphabet='0123456789+-() '))
        })
    )
    @settings(max_examples=100, deadline=None)
    def test_user_profile_update_round_trip(self, original_data, update_data, db_session):
        """
        **Feature: ai-patient-support-assistant, Property 1: User data round-trip consistency**
        
        For any profile update, storing the updated data then retrieving it 
        should return the updated values.
        
        This tests that:
        1. User profile can be updated
        2. Updated data persists correctly
        3. Only specified fields are updated
        4. Other fields remain unchanged
        """
        # Arrange: Create initial user
        password_hash = bcrypt.hashpw(original_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User(
            email=original_data['email'],
            password_hash=password_hash,
            first_name=original_data['first_name'],
            last_name=original_data['last_name'],
            date_of_birth=original_data['date_of_birth'],
            gender=original_data['gender'],
            phone_number=original_data['phone_number']
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        user_id = user.id
        original_email = user.email
        
        # Act: Update user profile
        if update_data['first_name'] is not None:
            user.first_name = update_data['first_name']
        if update_data['last_name'] is not None:
            user.last_name = update_data['last_name']
        if update_data['phone_number'] is not None:
            user.phone_number = update_data['phone_number']
        
        db_session.commit()
        db_session.expunge_all()
        
        # Act: Retrieve updated user
        retrieved_user = db_session.query(User).filter(User.id == user_id).first()
        
        # Assert: Updated fields match
        expected_first_name = update_data['first_name'] if update_data['first_name'] is not None else original_data['first_name']
        expected_last_name = update_data['last_name'] if update_data['last_name'] is not None else original_data['last_name']
        expected_phone = update_data['phone_number'] if update_data['phone_number'] is not None else original_data['phone_number']
        
        assert retrieved_user.first_name == expected_first_name, "First name should match updated value"
        assert retrieved_user.last_name == expected_last_name, "Last name should match updated value"
        assert retrieved_user.phone_number == expected_phone, "Phone number should match updated value"
        
        # Assert: Unchanged fields remain the same
        assert retrieved_user.email == original_email, "Email should not change"
        assert retrieved_user.date_of_birth == original_data['date_of_birth'], "Date of birth should not change"
        assert retrieved_user.gender == original_data['gender'], "Gender should not change"
        
        # Assert: Updated timestamp changed
        assert retrieved_user.updated_at is not None, "Updated timestamp should be set"
        
        # Cleanup
        db_session.delete(retrieved_user)
        db_session.commit()
    
    @given(user_data=user_profile_strategy())
    @settings(max_examples=50, deadline=None)
    def test_user_email_uniqueness(self, user_data, db_session):
        """
        Test that email uniqueness constraint is enforced.
        
        This ensures data integrity by preventing duplicate email addresses.
        """
        # Arrange: Create first user
        password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user1 = User(
            email=user_data['email'],
            password_hash=password_hash,
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        db_session.add(user1)
        db_session.commit()
        
        # Act & Assert: Try to create duplicate user
        user2 = User(
            email=user_data['email'],  # Same email
            password_hash=password_hash,
            first_name="Different",
            last_name="Name"
        )
        
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
        
        db_session.rollback()
        
        # Cleanup
        db_session.delete(user1)
        db_session.commit()
