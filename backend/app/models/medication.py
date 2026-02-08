"""Medication models"""
from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class Medication(Base):
    """Medication model"""
    __tablename__ = 'medications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(50))
    schedule_times = Column(JSONB)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, index=True)
    instructions = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    user = relationship('User', back_populates='medications')
    adherence_records = relationship('AdherenceRecord', back_populates='medication', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medication {self.name} - {self.dosage}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'schedule_times': self.schedule_times,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'instructions': self.instructions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AdherenceRecord(Base):
    """Adherence record model"""
    __tablename__ = 'adherence_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medication_id = Column(UUID(as_uuid=True), ForeignKey('medications.id', ondelete='CASCADE'), nullable=False, index=True)
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    taken_time = Column(DateTime(timezone=True), index=True)
    status = Column(String(20), nullable=False, index=True)  # 'taken', 'missed', 'skipped'
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    medication = relationship('Medication', back_populates='adherence_records')
    
    def __repr__(self):
        return f'<AdherenceRecord {self.medication_id} - {self.status}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'medication_id': str(self.medication_id),
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'taken_time': self.taken_time.isoformat() if self.taken_time else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
