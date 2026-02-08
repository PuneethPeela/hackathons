"""Symptom analysis routes"""
from flask import Blueprint, request, jsonify
from ..middleware.jwt_middleware import jwt_required_with_user, get_current_user
from ..middleware.audit_logger import log_audit
from ..services.medical_knowledge_service import MedicalKnowledgeService
from ..services.symptom_analysis_service import SymptomAnalysisService
from ..models import SymptomAnalysis, SessionLocal

bp = Blueprint('symptoms', __name__)
symptom_service = SymptomAnalysisService()


@bp.route('/search', methods=['GET'])
@jwt_required_with_user
def search_symptoms():
    """
    Search symptoms endpoint with autocomplete
    
    Query params:
        q: Search query
        limit: Max results (default 10)
    
    Returns:
        List of matching symptoms
    """
    try:
        current_user = get_current_user()
        
        # Get query parameter
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        if len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400
        
        limit = request.args.get('limit', 10, type=int)
        
        # Validate limit
        if limit > 50:
            limit = 50
        if limit < 1:
            limit = 10
        
        # Search symptoms in MongoDB
        symptoms = MedicalKnowledgeService.search_symptoms(query, limit=limit)
        
        # Format results
        formatted_symptoms = [
            {
                'name': symptom.get('name'),
                'description': symptom.get('description'),
                'severity': symptom.get('severity', 'unknown'),
                'common_diseases': symptom.get('common_diseases', [])[:3]  # Top 3
            }
            for symptom in symptoms
        ]
        
        # Audit log
        log_audit(
            user_id=current_user.id,
            action='search_symptoms',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={'query': query, 'results_count': len(formatted_symptoms)},
            success=True
        )
        
        return jsonify({
            'query': query,
            'results': formatted_symptoms,
            'count': len(formatted_symptoms)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error searching symptoms: {str(e)}'}), 500


@bp.route('/analyze', methods=['POST'])
@jwt_required_with_user
def analyze_symptoms():
    """
    Analyze symptoms endpoint
    
    Request body:
    {
        "symptoms": ["fever", "cough", "headache"],
        "age": 30,
        "gender": "male"
    }
    
    Returns:
        Analysis with possible conditions and recommendations
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Validate input
        if not data or 'symptoms' not in data:
            return jsonify({'error': 'Symptoms list is required'}), 400
        
        symptoms = data.get('symptoms', [])
        
        if not isinstance(symptoms, list):
            return jsonify({'error': 'Symptoms must be a list'}), 400
        
        if len(symptoms) == 0:
            return jsonify({'error': 'At least one symptom is required'}), 400
        
        if len(symptoms) > 20:
            return jsonify({'error': 'Maximum 20 symptoms allowed'}), 400
        
        # Optional demographic data
        age = data.get('age')
        gender = data.get('gender')
        
        # Perform symptom analysis
        analysis_result = symptom_service.analyze_symptoms(
            symptoms=symptoms,
            age=age,
            gender=gender
        )
        
        # Calculate risk severity
        risk_severity = symptom_service.calculate_risk_severity(
            analysis_result['predictions']
        )
        
        # Format results (top 3 predictions with confidence >= 0.6)
        formatted_predictions = symptom_service.format_analysis_results(
            predictions=analysis_result['predictions'],
            risk_severity=risk_severity,
            symptoms=symptoms
        )
        
        # Save analysis to database
        db = SessionLocal()
        try:
            symptom_analysis = SymptomAnalysis(
                user_id=current_user.id,
                symptoms=symptoms,
                predictions=formatted_predictions['predictions'],
                risk_level=risk_severity,
                confidence_score=analysis_result.get('avg_confidence', 0.0)
            )
            
            db.add(symptom_analysis)
            db.commit()
            db.refresh(symptom_analysis)
            
            analysis_id = symptom_analysis.id
            
        except Exception as e:
            db.rollback()
            print(f"Error saving symptom analysis: {e}")
            analysis_id = None
        finally:
            db.close()
        
        # Audit log
        log_audit(
            user_id=current_user.id,
            action='analyze_symptoms',
            resource_type='symptom_analysis',
            resource_id=analysis_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={
                'symptom_count': len(symptoms),
                'risk_level': risk_severity,
                'prediction_count': len(formatted_predictions['predictions'])
            },
            success=True
        )
        
        return jsonify({
            'analysis_id': analysis_id,
            'symptoms': symptoms,
            'risk_severity': risk_severity,
            'predictions': formatted_predictions['predictions'],
            'recommendations': formatted_predictions['recommendations'],
            'disclaimer': formatted_predictions['disclaimer']
        }), 200
        
    except Exception as e:
        # Audit log failure
        log_audit(
            user_id=current_user.id if current_user else None,
            action='analyze_symptoms',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details={'error': str(e)},
            success=False
        )
        
        return jsonify({'error': f'Error analyzing symptoms: {str(e)}'}), 500


@bp.route('/history', methods=['GET'])
@jwt_required_with_user
def get_symptom_history():
    """
    Get symptom analysis history for current user
    
    Query params:
        limit: Max results (default 20)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of past symptom analyses
    """
    try:
        current_user = get_current_user()
        
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate limits
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 20
        
        # Get analyses from database
        db = SessionLocal()
        try:
            analyses = db.query(SymptomAnalysis).filter(
                SymptomAnalysis.user_id == current_user.id
            ).order_by(
                SymptomAnalysis.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            formatted_analyses = [
                {
                    'id': analysis.id,
                    'symptoms': analysis.symptoms,
                    'risk_level': analysis.risk_level,
                    'confidence_score': analysis.confidence_score,
                    'predictions': analysis.predictions,
                    'created_at': analysis.created_at.isoformat()
                }
                for analysis in analyses
            ]
            
        finally:
            db.close()
        
        return jsonify({
            'analyses': formatted_analyses,
            'count': len(formatted_analyses),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving history: {str(e)}'}), 500
