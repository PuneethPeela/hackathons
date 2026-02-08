"""Authentication routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..services.auth_service import AuthService
from ..middleware.audit_logger import log_audit

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "phone_number": "+1234567890"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Profile data
        profile = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'date_of_birth': datetime.fromisoformat(data['date_of_birth']).date() if data.get('date_of_birth') else None,
            'gender': data.get('gender'),
            'phone_number': data.get('phone_number')
        }
        
        # Register user
        user, error = AuthService.register_user(email, password, profile)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Log audit event
        log_audit(
            user_id=str(user.id),
            action='user_registered',
            resource_type='user',
            resource_id=str(user.id),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user
        result, error = AuthService.authenticate(email, password)
        
        if error:
            # Log failed login attempt
            log_audit(
                user_id=None,
                action='login_failed',
                resource_type='user',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details={'email': email, 'reason': error},
                success=False
            )
            return jsonify({'error': error}), 401
        
        # Log successful login
        log_audit(
            user_id=result['user']['id'],
            action='login_success',
            resource_type='user',
            resource_id=result['user']['id'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Token refresh endpoint"""
    try:
        from flask_jwt_extended import create_access_token
        
        # Get user identity from refresh token
        user_id = get_jwt_identity()
        
        # Generate new access token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({'access_token': access_token}), 200
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile endpoint"""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Get user
        user = AuthService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile endpoint
    
    Request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890"
    }
    """
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle date conversion
        if 'date_of_birth' in data and data['date_of_birth']:
            data['date_of_birth'] = datetime.fromisoformat(data['date_of_birth']).date()
        
        # Update profile
        user, error = AuthService.update_profile(user_id, data)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Log audit event
        log_audit(
            user_id=user_id,
            action='profile_updated',
            resource_type='user',
            resource_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={'updated_fields': list(data.keys())}
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500
