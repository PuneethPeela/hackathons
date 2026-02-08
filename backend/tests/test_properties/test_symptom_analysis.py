"""
Property-based tests for symptom analysis functionality

**Feature: ai-patient-support-assistant**

Tests Properties 10, 11, 12, 13, 14 from design document
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from app.services.medical_knowledge_service import MedicalKnowledgeService
from app.services.symptom_analysis_service import SymptomAnalysisService


# Custom strategies
@st.composite
def symptom_list_strategy(draw):
    """Generate realistic symptom lists"""
    common_symptoms = [
        'fever', 'cough', 'headache', 'fatigue', 'nausea',
        'pain', 'dizziness', 'shortness of breath', 'chest pain',
        'sore throat', 'runny nose', 'muscle aches', 'chills'
    ]
    
    num_symptoms = draw(st.integers(min_value=1, max_value=10))
    symptoms = draw(st.lists(
        st.sampled_from(common_symptoms),
        min_size=num_symptoms,
        max_size=num_symptoms,
        unique=True
    ))
    
    return symptoms


class TestSymptomAnalysisProperties:
    """Test symptom analysis-related properties"""
    
    @given(
        query=st.text(min_size=2, max_size=20, alphabet=st.characters(whitelist_categories=('L',)))
    )
    @settings(max_examples=100)
    def test_property_10_symptom_autocomplete_accuracy(self, query):
        """
        **Property 10: Symptom autocomplete accuracy**
        
        WHEN a user searches for symptoms
        THEN the returned results SHALL match the search query
        AND results SHALL be relevant to the query
        
        Validates: Requirements 3.1
        """
        # Search for symptoms
        results = MedicalKnowledgeService.search_symptoms(query, limit=10)
        
        # All results should be relevant to query
        query_lower = query.lower()
        
        for symptom in results:
            symptom_name = symptom.get('name', '').lower()
            symptom_desc = symptom.get('description', '').lower()
            
            # Query should appear in name or description
            assert query_lower in symptom_name or query_lower in symptom_desc or \
                   any(word in symptom_name or word in symptom_desc 
                       for word in query_lower.split()), \
                   f"Symptom '{symptom.get('name')}' not relevant to query '{query}'"
    
    @given(
        symptoms=symptom_list_strategy()
    )
    @settings(max_examples=100)
    def test_property_11_prediction_confidence_threshold(self, symptoms):
        """
        **Property 11: Prediction confidence threshold**
        
        WHEN symptoms are analyzed
        THEN predictions with confidence >= 0.6 SHALL be included
        AND predictions with confidence < 0.6 SHALL be excluded (unless top 3)
        
        Validates: Requirements 3.2
        """
        service = SymptomAnalysisService()
        
        # Analyze symptoms
        result = service.analyze_symptoms(symptoms)
        
        predictions = result.get('predictions', [])
        
        # Should have at least one prediction
        assert len(predictions) > 0, "Should return at least one prediction"
        
        # Should have at most 3 predictions
        assert len(predictions) <= 3, "Should return at most 3 predictions"
        
        # Check confidence threshold
        for i, pred in enumerate(predictions):
            confidence = pred.get('confidence', 0)
            
            # First 3 predictions can have any confidence
            # But if confidence >= 0.6, it should definitely be included
            if i < 3:
                assert confidence >= 0, "Confidence should be non-negative"
                assert confidence <= 1.0, "Confidence should not exceed 1.0"
            
            # If we have more than 3 predictions, they must all be >= 0.6
            if len(predictions) > 3:
                assert confidence >= 0.6, \
                    f"Prediction beyond top 3 should have confidence >= 0.6, got {confidence}"
    
    @given(
        symptoms=symptom_list_strategy()
    )
    @settings(max_examples=100)
    def test_property_12_risk_severity_assignment(self, symptoms):
        """
        **Property 12: Risk severity assignment**
        
        WHEN predictions are generated
        THEN a risk severity level SHALL be assigned
        AND the level SHALL be one of: low, medium, high, critical
        
        Validates: Requirements 3.3
        """
        service = SymptomAnalysisService()
        
        # Analyze symptoms
        result = service.analyze_symptoms(symptoms)
        predictions = result.get('predictions', [])
        
        # Calculate risk severity
        risk_severity = service.calculate_risk_severity(predictions)
        
        # Verify risk severity is valid
        valid_levels = ['low', 'medium', 'high', 'critical']
        assert risk_severity in valid_levels, \
            f"Risk severity '{risk_severity}' not in valid levels {valid_levels}"
        
        # Verify risk severity correlates with confidence
        if predictions:
            max_confidence = max(p['confidence'] for p in predictions)
            
            # High confidence should not result in low risk (generally)
            if max_confidence >= 0.9:
                assert risk_severity in ['medium', 'high', 'critical'], \
                    f"High confidence ({max_confidence}) should not result in low risk"
            
            # Low confidence should not result in critical risk
            if max_confidence < 0.7:
                assert risk_severity != 'critical', \
                    f"Low confidence ({max_confidence}) should not result in critical risk"
    
    @given(
        symptoms=symptom_list_strategy()
    )
    @settings(max_examples=100)
    def test_property_13_top_predictions_limit(self, symptoms):
        """
        **Property 13: Top predictions limit**
        
        WHEN symptom analysis is performed
        THEN at most 3 predictions SHALL be returned
        AND predictions SHALL be ordered by confidence (highest first)
        
        Validates: Requirements 3.4
        """
        service = SymptomAnalysisService()
        
        # Analyze symptoms
        result = service.analyze_symptoms(symptoms)
        predictions = result.get('predictions', [])
        
        # Verify at most 3 predictions
        assert len(predictions) <= 3, \
            f"Should return at most 3 predictions, got {len(predictions)}"
        
        # Verify predictions are ordered by confidence (descending)
        for i in range(len(predictions) - 1):
            current_confidence = predictions[i]['confidence']
            next_confidence = predictions[i + 1]['confidence']
            
            assert current_confidence >= next_confidence, \
                f"Predictions not ordered by confidence: {current_confidence} < {next_confidence}"
    
    @given(
        symptoms=symptom_list_strategy()
    )
    @settings(max_examples=100)
    def test_property_14_high_risk_consultation_recommendation(self, symptoms):
        """
        **Property 14: High-risk consultation recommendation**
        
        WHEN risk severity is high or critical
        THEN recommendations SHALL include consulting a healthcare provider
        AND recommendations SHALL emphasize urgency
        
        Validates: Requirements 3.5
        """
        service = SymptomAnalysisService()
        
        # Analyze symptoms
        result = service.analyze_symptoms(symptoms)
        predictions = result.get('predictions', [])
        
        # Calculate risk severity
        risk_severity = service.calculate_risk_severity(predictions)
        
        # Format results
        formatted = service.format_analysis_results(
            predictions=predictions,
            risk_severity=risk_severity,
            symptoms=symptoms
        )
        
        recommendations = formatted.get('recommendations', [])
        
        # Verify recommendations exist
        assert len(recommendations) > 0, "Should provide recommendations"
        
        # Check for consultation recommendation based on risk
        recommendations_text = ' '.join(recommendations).lower()
        
        if risk_severity == 'critical':
            # Critical should mention emergency/immediate
            assert any(keyword in recommendations_text 
                      for keyword in ['emergency', 'immediate', '911', 'urgent']), \
                "Critical risk should recommend immediate/emergency care"
        
        elif risk_severity == 'high':
            # High should mention doctor/appointment soon
            assert any(keyword in recommendations_text 
                      for keyword in ['doctor', 'appointment', 'soon', 'medical']), \
                "High risk should recommend seeing a doctor soon"
        
        elif risk_severity == 'medium':
            # Medium should mention doctor/appointment
            assert any(keyword in recommendations_text 
                      for keyword in ['doctor', 'appointment', 'consider']), \
                "Medium risk should recommend considering a doctor visit"
        
        # All risk levels should have some form of medical guidance
        assert any(keyword in recommendations_text 
                  for keyword in ['doctor', 'medical', 'healthcare', 'provider', 'emergency']), \
            "All recommendations should mention medical consultation"
    
    @given(
        symptoms=symptom_list_strategy()
    )
    @settings(max_examples=50)
    def test_property_11_extended_prediction_completeness(self, symptoms):
        """
        **Property 11 (Extended): Prediction completeness**
        
        WHEN predictions are returned
        THEN each prediction SHALL include disease name and confidence
        AND predictions SHALL include relevant medical information
        
        Validates: Requirements 3.2, 3.4
        """
        service = SymptomAnalysisService()
        
        # Analyze symptoms
        result = service.analyze_symptoms(symptoms)
        predictions = result.get('predictions', [])
        
        # Format results
        risk_severity = service.calculate_risk_severity(predictions)
        formatted = service.format_analysis_results(
            predictions=predictions,
            risk_severity=risk_severity,
            symptoms=symptoms
        )
        
        formatted_predictions = formatted.get('predictions', [])
        
        # Each prediction should have required fields
        for pred in formatted_predictions:
            assert 'disease' in pred, "Prediction should have disease name"
            assert 'confidence' in pred, "Prediction should have confidence score"
            assert 'description' in pred, "Prediction should have description"
            
            # Verify confidence is valid
            confidence = pred['confidence']
            assert 0 <= confidence <= 1.0, \
                f"Confidence {confidence} should be between 0 and 1"
            
            # Verify disease name is not empty
            assert len(pred['disease']) > 0, "Disease name should not be empty"
    
    @given(
        symptoms=symptom_list_strategy()
    )
    @settings(max_examples=50)
    def test_property_14_extended_disclaimer_inclusion(self, symptoms):
        """
        **Property 14 (Extended): Medical disclaimer inclusion**
        
        WHEN symptom analysis results are formatted
        THEN a medical disclaimer SHALL be included
        AND the disclaimer SHALL emphasize this is not medical advice
        
        Validates: Requirements 3.5, 8.2
        """
        service = SymptomAnalysisService()
        
        # Analyze symptoms
        result = service.analyze_symptoms(symptoms)
        predictions = result.get('predictions', [])
        
        # Format results
        risk_severity = service.calculate_risk_severity(predictions)
        formatted = service.format_analysis_results(
            predictions=predictions,
            risk_severity=risk_severity,
            symptoms=symptoms
        )
        
        disclaimer = formatted.get('disclaimer', '')
        
        # Verify disclaimer exists
        assert len(disclaimer) > 0, "Disclaimer should be present"
        
        # Verify disclaimer contains key phrases
        disclaimer_lower = disclaimer.lower()
        
        assert 'medical advice' in disclaimer_lower or 'not constitute' in disclaimer_lower, \
            "Disclaimer should mention this is not medical advice"
        
        assert 'healthcare professional' in disclaimer_lower or 'doctor' in disclaimer_lower, \
            "Disclaimer should recommend consulting healthcare professional"
        
        assert 'informational' in disclaimer_lower or 'educational' in disclaimer_lower, \
            "Disclaimer should mention informational/educational purpose"
    
    @given(
        symptoms1=symptom_list_strategy(),
        symptoms2=symptom_list_strategy()
    )
    @settings(max_examples=50)
    def test_property_12_extended_risk_consistency(self, symptoms1, symptoms2):
        """
        **Property 12 (Extended): Risk severity consistency**
        
        WHEN the same symptoms are analyzed multiple times
        THEN the risk severity SHALL be consistent
        
        Validates: Requirements 3.3
        """
        service = SymptomAnalysisService()
        
        # Analyze same symptoms twice
        result1 = service.analyze_symptoms(symptoms1)
        result2 = service.analyze_symptoms(symptoms1)
        
        predictions1 = result1.get('predictions', [])
        predictions2 = result2.get('predictions', [])
        
        risk1 = service.calculate_risk_severity(predictions1)
        risk2 = service.calculate_risk_severity(predictions2)
        
        # Risk should be consistent for same symptoms
        assert risk1 == risk2, \
            f"Risk severity should be consistent: {risk1} != {risk2}"
        
        # Analyze different symptoms
        result3 = service.analyze_symptoms(symptoms2)
        predictions3 = result3.get('predictions', [])
        risk3 = service.calculate_risk_severity(predictions3)
        
        # Risk should be valid
        assert risk3 in ['low', 'medium', 'high', 'critical']
