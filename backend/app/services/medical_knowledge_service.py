"""
Medical Knowledge Service for retrieving information from MongoDB
"""
from typing import List, Dict, Optional
from ..mongodb.connection import get_mongodb


class MedicalKnowledgeService:
    """Service for querying medical knowledge base"""
    
    @staticmethod
    def search_diseases(query: str, limit: int = 5) -> List[Dict]:
        """
        Search for diseases by name or symptoms
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching diseases
        """
        db = get_mongodb()
        collection = db['medical_knowledge']
        
        # Text search on name and description
        results = collection.find(
            {
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}},
                    {'symptoms': {'$regex': query, '$options': 'i'}}
                ]
            }
        ).limit(limit)
        
        return list(results)
    
    @staticmethod
    def get_disease_by_name(disease_name: str) -> Optional[Dict]:
        """
        Get disease information by exact name
        
        Args:
            disease_name: Disease name
        
        Returns:
            Disease document or None
        """
        db = get_mongodb()
        collection = db['medical_knowledge']
        
        disease = collection.find_one(
            {'name': {'$regex': f'^{disease_name}$', '$options': 'i'}}
        )
        
        return disease
    
    @staticmethod
    def get_disease_by_icd_code(icd_code: str) -> Optional[Dict]:
        """
        Get disease by ICD code
        
        Args:
            icd_code: ICD-10 code
        
        Returns:
            Disease document or None
        """
        db = get_mongodb()
        collection = db['medical_knowledge']
        
        disease = collection.find_one({'icd_code': icd_code})
        
        return disease
    
    @staticmethod
    def format_disease_for_ai(disease: Dict) -> str:
        """
        Format disease information for AI context
        
        Args:
            disease: Disease document
        
        Returns:
            Formatted string for AI
        """
        if not disease:
            return ""
        
        formatted = f"""
**Disease: {disease.get('name', 'Unknown')}**

Description: {disease.get('description', 'No description available')}

Common Symptoms:
{', '.join(disease.get('symptoms', []))}

Treatment Options:
{', '.join(disease.get('treatment_options', []))}

Lifestyle Recommendations:
{', '.join(disease.get('lifestyle_recommendations', []))}

When to See a Doctor:
{disease.get('when_to_see_doctor', 'Consult a healthcare provider if symptoms persist or worsen')}
"""
        
        return formatted.strip()
    
    @staticmethod
    def get_treatment_guidelines(condition: str) -> Optional[Dict]:
        """
        Get treatment guidelines for a condition
        
        Args:
            condition: Medical condition
        
        Returns:
            Treatment guidelines or None
        """
        db = get_mongodb()
        collection = db['treatment_guidelines']
        
        guideline = collection.find_one(
            {'condition': {'$regex': condition, '$options': 'i'}}
        )
        
        return guideline
    
    @staticmethod
    def format_treatment_guidelines(guideline: Dict) -> str:
        """
        Format treatment guidelines for AI context
        
        Args:
            guideline: Treatment guideline document
        
        Returns:
            Formatted string
        """
        if not guideline:
            return ""
        
        formatted = f"""
**Treatment Guidelines for {guideline.get('condition', 'Unknown')}**

Recommended Treatments:
"""
        
        for treatment in guideline.get('recommended_treatments', []):
            formatted += f"- {treatment}\n"
        
        if guideline.get('lifestyle_modifications'):
            formatted += "\nLifestyle Modifications:\n"
            for mod in guideline['lifestyle_modifications']:
                formatted += f"- {mod}\n"
        
        if guideline.get('monitoring'):
            formatted += f"\nMonitoring: {guideline['monitoring']}\n"
        
        if guideline.get('follow_up'):
            formatted += f"\nFollow-up: {guideline['follow_up']}\n"
        
        return formatted.strip()
    
    @staticmethod
    def search_symptoms(query: str, limit: int = 10) -> List[Dict]:
        """
        Search symptom database
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching symptoms
        """
        db = get_mongodb()
        collection = db['symptom_database']
        
        results = collection.find(
            {
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]
            }
        ).limit(limit)
        
        return list(results)
    
    @staticmethod
    def get_symptom_correlations(symptom_name: str) -> List[str]:
        """
        Get diseases commonly associated with a symptom
        
        Args:
            symptom_name: Symptom name
        
        Returns:
            List of associated disease names
        """
        db = get_mongodb()
        collection = db['symptom_database']
        
        symptom = collection.find_one(
            {'name': {'$regex': f'^{symptom_name}$', '$options': 'i'}}
        )
        
        if symptom and 'common_diseases' in symptom:
            return symptom['common_diseases']
        
        return []
    
    @staticmethod
    def get_lab_test_standards(test_name: str) -> Optional[Dict]:
        """
        Get standard ranges for a lab test
        
        Args:
            test_name: Lab test name
        
        Returns:
            Lab test standards or None
        """
        db = get_mongodb()
        collection = db['lab_test_standards']
        
        test = collection.find_one(
            {'test_name': {'$regex': test_name, '$options': 'i'}}
        )
        
        return test
    
    @staticmethod
    def interpret_lab_value(test_name: str, value: float, unit: str) -> Dict:
        """
        Interpret a lab test value
        
        Args:
            test_name: Lab test name
            value: Test value
            unit: Unit of measurement
        
        Returns:
            Interpretation dict
        """
        test_standard = MedicalKnowledgeService.get_lab_test_standards(test_name)
        
        if not test_standard:
            return {
                'status': 'unknown',
                'message': 'No standard range available for this test'
            }
        
        # Check if unit matches
        if test_standard.get('unit') != unit:
            return {
                'status': 'error',
                'message': f"Unit mismatch. Expected {test_standard.get('unit')}, got {unit}"
            }
        
        # Get ranges
        normal_min = test_standard.get('normal_range', {}).get('min')
        normal_max = test_standard.get('normal_range', {}).get('max')
        
        # Interpret value
        if normal_min is not None and value < normal_min:
            severity = 'critical' if value < normal_min * 0.5 else 'low'
            return {
                'status': severity,
                'message': f'{test_name} is below normal range',
                'interpretation': test_standard.get('low_interpretation', 'Value is low'),
                'recommendation': 'Consult your healthcare provider'
            }
        elif normal_max is not None and value > normal_max:
            severity = 'critical' if value > normal_max * 1.5 else 'high'
            return {
                'status': severity,
                'message': f'{test_name} is above normal range',
                'interpretation': test_standard.get('high_interpretation', 'Value is high'),
                'recommendation': 'Consult your healthcare provider'
            }
        else:
            return {
                'status': 'normal',
                'message': f'{test_name} is within normal range',
                'interpretation': 'Your result is normal',
                'recommendation': 'Continue maintaining healthy habits'
            }
    
    @staticmethod
    def get_relevant_context_for_query(query: str) -> str:
        """
        Get relevant medical context for a user query
        
        Args:
            query: User's question or message
        
        Returns:
            Formatted medical context string
        """
        context_parts = []
        
        # Search for relevant diseases
        diseases = MedicalKnowledgeService.search_diseases(query, limit=2)
        for disease in diseases:
            context_parts.append(MedicalKnowledgeService.format_disease_for_ai(disease))
        
        # Search for treatment guidelines
        db = get_mongodb()
        guidelines_collection = db['treatment_guidelines']
        guidelines = guidelines_collection.find(
            {
                '$or': [
                    {'condition': {'$regex': query, '$options': 'i'}},
                    {'recommended_treatments': {'$regex': query, '$options': 'i'}}
                ]
            }
        ).limit(1)
        
        for guideline in guidelines:
            context_parts.append(MedicalKnowledgeService.format_treatment_guidelines(guideline))
        
        if context_parts:
            return "\n\n---\n\n".join(context_parts)
        
        return ""
    
    @staticmethod
    def get_all_diseases(limit: int = 100, skip: int = 0) -> List[Dict]:
        """
        Get all diseases (for admin/testing)
        
        Args:
            limit: Maximum results
            skip: Number to skip
        
        Returns:
            List of diseases
        """
        db = get_mongodb()
        collection = db['medical_knowledge']
        
        diseases = collection.find().skip(skip).limit(limit)
        
        return list(diseases)
    
    @staticmethod
    def get_database_stats() -> Dict:
        """
        Get statistics about medical knowledge database
        
        Returns:
            Stats dict
        """
        db = get_mongodb()
        
        return {
            'diseases_count': db['medical_knowledge'].count_documents({}),
            'symptoms_count': db['symptom_database'].count_documents({}),
            'treatment_guidelines_count': db['treatment_guidelines'].count_documents({}),
            'lab_tests_count': db['lab_test_standards'].count_documents({})
        }
