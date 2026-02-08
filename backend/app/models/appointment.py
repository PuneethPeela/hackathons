"""Appointment and treatment models"""
from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class Appointment(Base):
    """Appointment model"""
    __tablename__ = 'appointments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    appointment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    location = Column(String(255))
    doctor_name = Column(String(100))
    specialty = Column(String(100))
    status = Column(String(20), default='scheduled', index=True)  # 'scheduled', 'completed', 'cancelled', 'rescheduled'
    reminder_sent = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship('User', back_populates='appointments')
    
    def __repr__(self):
        return f'<Appointment {self.title} - {self.appointment_date}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'description': self.description,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'location': self.location,
            'doctor_name': self.doctor_name,
            'specialty': self.specialty,
            'status': self.status,
            'reminder_sent': self.reminder_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TreatmentMilestone(Base):
    """Treatment milestone model"""
    __tablename__ = 'treatment_milestones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_date = Column(Date, index=True)
    completed = Column(Boolean, default=False, index=True)
    completed_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship('User', back_populates='treatment_milestones')
    
    def __repr__(self):
        return f'<TreatmentMilestone {self.title}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completed': self.completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
