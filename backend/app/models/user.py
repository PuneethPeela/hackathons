"""User model"""
from sqlalchemy import Column, String, Date, DateTime, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    phone_number = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))
    
    # Relationships
    medications = relationship('Medication', back_populates='user', cascade='all, delete-orphan')
    appointments = relationship('Appointment', back_populates='user', cascade='all, delete-orphan')
    lab_reports = relationship('LabReport', back_populates='user', cascade='all, delete-orphan')
    conversations = relationship('Conversation', back_populates='user', cascade='all, delete-orphan')
    symptom_analyses = relationship('SymptomAnalysis', back_populates='user', cascade='all, delete-orphan')
    treatment_milestones = relationship('TreatmentMilestone', back_populates='user', cascade='all, delete-orphan')
    device_tokens = relationship('DeviceToken', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.email
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            from datetime import datetime
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
        }
        
        if include_sensitive:
            data['last_login'] = self.last_login.isoformat() if self.last_login else None
            data['failed_login_attempts'] = self.failed_login_attempts
            
        return data
