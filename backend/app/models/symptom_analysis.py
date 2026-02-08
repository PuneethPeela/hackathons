"""Symptom analysis model"""
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class SymptomAnalysis(Base):
    """Symptom analysis model"""
    __tablename__ = 'symptom_analyses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    symptoms = Column(JSONB, nullable=False)
    predictions = Column(JSONB, nullable=False)
    risk_severity = Column(String(20), nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'
    recommended_action = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship('User', back_populates='symptom_analyses')
    
    def __repr__(self):
        return f'<SymptomAnalysis {self.id} - {self.risk_severity}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'symptoms': self.symptoms,
            'predictions': self.predictions,
            'risk_severity': self.risk_severity,
            'recommended_action': self.recommended_action,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
