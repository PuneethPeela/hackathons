"""JWT token validation middleware"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, RevokedTokenError
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from ..models import User, SessionLocal


def jwt_required_with_user(fn):
    """
    Decorator that validates JWT token and loads user
    
    Usage:
        @bp.route('/protected')
        @jwt_required_with_user
        def protected_route(current_user):
            return {'user_id': current_user.id}
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            
            # Load user from database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                if not user.is_active:
                    return jsonify({'error': 'Account is inactive'}), 403
                
                # Pass user to the route function
                return fn(current_user=user, *args, **kwargs)
                
            finally:
                db.close()
                
        except ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except NoAuthorizationError:
            return jsonify({'error': 'Missing authorization header'}), 401
        except InvalidHeaderError:
            return jsonify({'error': 'Invalid authorization header'}), 401
        except RevokedTokenError:
            return jsonify({'error': 'Token has been revoked'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    
    return wrapper


def optional_jwt_with_user(fn):
    """
    Decorator that optionally validates JWT token
    If token is present and valid, loads user; otherwise continues without user
    
    Usage:
        @bp.route('/optional-protected')
        @optional_jwt_with_user
        def optional_route(current_user=None):
            if current_user:
                return {'user_id': current_user.id}
            return {'message': 'Anonymous access'}
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Try to verify JWT token
            verify_jwt_in_request(optional=True)
            
            # Get user ID from token if present
            user_id = get_jwt_identity()
            
            if user_id:
                # Load user from database
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    
                    if user and user.is_active:
                        return fn(current_user=user, *args, **kwargs)
                finally:
                    db.close()
            
            # No valid token or user, continue without user
            return fn(current_user=None, *args, **kwargs)
            
        except Exception:
            # Any error, continue without user
            return fn(current_user=None, *args, **kwargs)
    
    return wrapper


def admin_required(fn):
    """
    Decorator that requires admin role
    
    Usage:
        @bp.route('/admin-only')
        @admin_required
        def admin_route(current_user):
            return {'message': 'Admin access granted'}
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get JWT claims
            claims = get_jwt()
            
            # Check for admin role
            if claims.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            # Get user ID
            user_id = get_jwt_identity()
            
            # Load user
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user or not user.is_active:
                    return jsonify({'error': 'User not found or inactive'}), 403
                
                return fn(current_user=user, *args, **kwargs)
                
            finally:
                db.close()
                
        except Exception as e:
            return jsonify({'error': f'Authorization failed: {str(e)}'}), 401
    
    return wrapper


def get_current_user_id() -> str:
    """
    Helper function to get current user ID from JWT token
    
    Returns:
        User ID string
    
    Raises:
        Exception if no valid token
    """
    return get_jwt_identity()


def get_current_user() -> User:
    """
    Helper function to get current user object from JWT token
    
    Returns:
        User object
    
    Raises:
        Exception if no valid token or user not found
    """
    user_id = get_jwt_identity()
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise Exception("User not found")
        
        if not user.is_active:
            raise Exception("User is inactive")
        
        return user
    finally:
        db.close()
