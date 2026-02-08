"""
AI-Based Patient Support Assistant - Backend Application
"""
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from .config import Config

jwt = JWTManager()


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    jwt.init_app(app)
    
    # Configure TLS/HTTPS security
    # Talisman enforces HTTPS, sets security headers
    if not app.config.get('TESTING', False):
        # Only enforce HTTPS in production
        csp = {
            'default-src': "'self'",
            'script-src': "'self'",
            'style-src': "'self' 'unsafe-inline'",
            'img-src': "'self' data: https:",
            'font-src': "'self'",
            'connect-src': "'self'",
        }
        
        Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,  # 1 year
            content_security_policy=csp,
            content_security_policy_nonce_in=['script-src'],
            feature_policy={
                'geolocation': "'none'",
                'camera': "'none'",
                'microphone': "'none'",
            }
        )
    
    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        """Add additional security headers"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove server header
        response.headers.pop('Server', None)
        
        return response
    
    # Register blueprints
    from .routes import auth, chat, symptoms, lab_reports, medications, appointments, notifications
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(chat.bp, url_prefix='/api/chat')
    app.register_blueprint(symptoms.bp, url_prefix='/api/symptoms')
    app.register_blueprint(lab_reports.bp, url_prefix='/api/lab-reports')
    app.register_blueprint(medications.bp, url_prefix='/api/medications')
    app.register_blueprint(appointments.bp, url_prefix='/api/appointments')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
    
    return app
