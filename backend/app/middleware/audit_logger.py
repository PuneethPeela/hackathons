"""Audit logging middleware"""
from datetime import datetime
from typing import Optional, Dict
from ..models import AuditLog, SessionLocal


def log_audit(
    user_id: Optional[str],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict] = None,
    success: bool = True
):
    """
    Log an audit event
    
    Args:
        user_id: User ID performing the action
        action: Action being performed
        resource_type: Type of resource being accessed
        resource_id: ID of resource being accessed
        ip_address: IP address of request
        user_agent: User agent string
        details: Additional details as JSON
        success: Whether the action was successful
    """
    db = SessionLocal()
    
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            success=success
        )
        
        db.add(audit_log)
        db.commit()
        
    except Exception as e:
        db.rollback()
        # Log error but don't fail the request
        print(f"Audit logging failed: {e}")
    finally:
        db.close()
