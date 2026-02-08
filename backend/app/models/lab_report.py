"""Lab report model"""
from sqlalchemy import Column, String, Date, DateTime, Integer, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from .database import Base


class LabReport(Base):
    """Lab report model"""
    __tablename__ = 'lab_reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    report_date = Column(Date, index=True)
    extracted_data = Column(JSONB)
    analysis_results = Column(JSONB)
    processing_status = Column(String(20), default='pending', index=True)  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship('User', back_populates='lab_reports')
    
    def __repr__(self):
        return f'<LabReport {self.file_name} - {self.processing_status}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'extracted_data': self.extracted_data,
            'analysis_results': self.analysis_results,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
        }
