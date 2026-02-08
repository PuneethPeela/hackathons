"""MongoDB repository classes for data access"""
from .connection import get_mongodb
from typing import List, Dict, Optional
from datetime import datetime


class MedicalKnowledgeRepository:
    """Repository for medical knowledge base"""
    
    def __init__(self):
        self.db = get_mongodb()
        self.collection = self.db.medical_knowledge
    
    def find_by_disease_name(self, disease_name: str) -> Optional[Dict]:
        """Find disease information by name"""
        return self.collection.find_one({'disease_name': disease_name})
    
    def search_diseases(self, query: str, limit: int = 10) -> List[Dict]:
        """Search diseases by text"""
        return list(self.collection.find(
            {'$text': {'$search': query}}
        ).limit(limit))
    
    def find_by_category(self, category: str) -> List[Dict]:
        """Find diseases by category"""
        return list(self.collection.find({'category': category}))
    
    def insert_disease(self, disease_data: Dict) -> str:
        """Insert new disease information"""
        disease_data['last_updated'] = datetime.utcnow()
        result = self.collection.insert_one(disease_data)
        return str(result.inserted_id)
    
    def update_disease(self, disease_name: str, update_data: Dict) -> bool:
        """Update disease information"""
        update_data['last_updated'] = datetime.utcnow()
        result = self.collection.update_one(
            {'disease_name': disease_name},
            {'$set': update_data}
        )
        return result.modified_count > 0


class SymptomRepository:
    """Repository for symptom database"""
    
    def __init__(self):
        self.db = get_mongodb()
        self.collection = self.db.symptoms
    
    def find_by_name(self, symptom_name: str) -> Optional[Dict]:
        """Find symptom by name"""
        return self.collection.find_one({'symptom_name': symptom_name})
    
    def search_symptoms(self, query: str, limit: int = 20) -> List[Dict]:
        """Search symptoms by text (autocomplete)"""
        # Use regex for prefix matching
        regex_pattern = f'^{query}'
        results = list(self.collection.find(
            {'symptom_name': {'$regex': regex_pattern, '$options': 'i'}}
        ).limit(limit))
        
        # Also search in synonyms
        synonym_results = list(self.collection.find(
            {'synonyms': {'$regex': regex_pattern, '$options': 'i'}}
        ).limit(limit))
        
        # Combine and deduplicate
        all_results = {str(r['_id']): r for r in results + synonym_results}
        return list(all_results.values())[:limit]
    
    def find_by_category(self, category: str) -> List[Dict]:
        """Find symptoms by category"""
        return list(self.collection.find({'category': category}))
    
    def get_associated_diseases(self, symptom_name: str) -> List[Dict]:
        """Get diseases associated with a symptom"""
        symptom = self.find_by_name(symptom_name)
        if symptom and 'associated_diseases' in symptom:
            return symptom['associated_diseases']
        return []
    
    def insert_symptom(self, symptom_data: Dict) -> str:
        """Insert new symptom"""
        result = self.collection.insert_one(symptom_data)
        return str(result.inserted_id)


class TreatmentGuidelineRepository:
    """Repository for treatment guidelines"""
    
    def __init__(self):
        self.db = get_mongodb()
        self.collection = self.db.treatment_guidelines
    
    def find_by_condition(self, condition: str) -> List[Dict]:
        """Find treatment guidelines by condition"""
        return list(self.collection.find({'condition': condition}))
    
    def find_latest_by_condition(self, condition: str) -> Optional[Dict]:
        """Find latest treatment guideline for a condition"""
        return self.collection.find_one(
            {'condition': condition},
            sort=[('publication_date', -1)]
        )
    
    def insert_guideline(self, guideline_data: Dict) -> str:
        """Insert new treatment guideline"""
        result = self.collection.insert_one(guideline_data)
        return str(result.inserted_id)


class LabTestStandardRepository:
    """Repository for lab test standards"""
    
    def __init__(self):
        self.db = get_mongodb()
        self.collection = self.db.lab_test_standards
    
    def find_by_test_name(self, test_name: str) -> Optional[Dict]:
        """Find lab test standard by name"""
        return self.collection.find_one({'test_name': test_name})
    
    def find_by_test_code(self, test_code: str) -> Optional[Dict]:
        """Find lab test standard by code"""
        return self.collection.find_one({'test_code': test_code})
    
    def search_tests(self, query: str, limit: int = 20) -> List[Dict]:
        """Search lab tests"""
        regex_pattern = f'{query}'
        return list(self.collection.find(
            {'test_name': {'$regex': regex_pattern, '$options': 'i'}}
        ).limit(limit))
    
    def find_by_category(self, category: str) -> List[Dict]:
        """Find lab tests by category"""
        return list(self.collection.find({'category': category}))
    
    def get_reference_range(self, test_name: str, age_group: str = None, gender: str = None) -> Optional[Dict]:
        """Get reference range for a test"""
        test = self.find_by_test_name(test_name)
        if not test or 'reference_ranges' not in test:
            return None
        
        # Find matching reference range
        for ref_range in test['reference_ranges']:
            if age_group and ref_range.get('age_group') != age_group:
                continue
            if gender and ref_range.get('gender') != gender:
                continue
            return ref_range
        
        # Return first range if no specific match
        return test['reference_ranges'][0] if test['reference_ranges'] else None
    
    def insert_test_standard(self, test_data: Dict) -> str:
        """Insert new lab test standard"""
        result = self.collection.insert_one(test_data)
        return str(result.inserted_id)
