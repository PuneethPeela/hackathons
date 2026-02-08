"""Authentication service"""
import bcrypt
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError
from ..models import User, SessionLocal
from ..utils.encryption import encrypt_field


class AuthService:
    """Service for user authentication and authorization"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength
        Requirements: At least 8 characters, 1 uppercase, 1 lowercase, 1 number
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def register_user(email: str, password: str, profile: Dict) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user
        
        Args:
            email: User email
            password: Plain text password
            profile: User profile data (first_name, last_name, etc.)
        
        Returns:
            Tuple of (User object, error message)
        """
        db = SessionLocal()
        
        try:
            # Validate email
            is_valid, error = AuthService.validate_email(email)
            if not is_valid:
                return None, error
            
            # Validate password
            is_valid, error = AuthService.validate_password(password)
            if not is_valid:
                return None, error
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                return None, "Email already registered"
            
            # Hash password
            password_hash = AuthService.hash_password(password)
            
            # Encrypt sensitive fields if provided
            phone_number = profile.get('phone_number')
            if phone_number:
                phone_number = encrypt_field(phone_number)
            
            # Create user
            user = User(
                email=email,
                password_hash=password_hash,
                first_name=profile.get('first_name'),
                last_name=profile.get('last_name'),
                date_of_birth=profile.get('date_of_birth'),
                gender=profile.get('gender'),
                phone_number=phone_number
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user, None
            
        except IntegrityError:
            db.rollback()
            return None, "Email already registered"
        except Exception as e:
            db.rollback()
            return None, f"Registration failed: {str(e)}"
        finally:
            db.close()
    
    @staticmethod
    def authenticate(email: str, password: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Authenticate user and generate tokens
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            Tuple of (token dict, error message)
        """
        db = SessionLocal()
        
        try:
            # Find user
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                return None, "Invalid email or password"
            
            # Check if account is locked
            if user.is_account_locked():
                lock_time_remaining = (user.account_locked_until - datetime.utcnow()).total_seconds() / 60
                return None, f"Account is locked. Try again in {int(lock_time_remaining)} minutes"
            
            # Check if account is active
            if not user.is_active:
                return None, "Account is inactive"
            
            # Verify password
            if not AuthService.verify_password(password, user.password_hash):
                # Increment failed login attempts
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
                    db.commit()
                    return None, "Account locked due to too many failed login attempts"
                
                db.commit()
                return None, "Invalid email or password"
            
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.account_locked_until = None
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Generate tokens
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={'email': user.email}
            )
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }, None
            
        except Exception as e:
            return None, f"Authentication failed: {str(e)}"
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    @staticmethod
    def update_profile(user_id: str, profile_data: Dict) -> Tuple[Optional[User], Optional[str]]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            profile_data: Profile fields to update
        
        Returns:
            Tuple of (User object, error message)
        """
        db = SessionLocal()
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None, "User not found"
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'phone_number']
            
            for field in allowed_fields:
                if field in profile_data:
                    value = profile_data[field]
                    
                    # Encrypt sensitive fields
                    if field == 'phone_number' and value:
                        value = encrypt_field(value)
                    
                    setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            return user, None
            
        except Exception as e:
            db.rollback()
            return None, f"Profile update failed: {str(e)}"
        finally:
            db.close()
