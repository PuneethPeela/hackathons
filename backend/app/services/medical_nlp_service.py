"""
Medical NLP Service for text simplification and readability
"""
import re
from typing import Dict, List, Tuple
import textstat


class MedicalNLPService:
    """Service for medical text processing and simplification"""
    
    # Medical term dictionary (common terms and their simple explanations)
    MEDICAL_TERMS = {
        'hypertension': 'high blood pressure',
        'hypotension': 'low blood pressure',
        'tachycardia': 'fast heart rate',
        'bradycardia': 'slow heart rate',
        'dyspnea': 'difficulty breathing',
        'edema': 'swelling',
        'pruritus': 'itching',
        'pyrexia': 'fever',
        'cephalgia': 'headache',
        'myalgia': 'muscle pain',
        'arthralgia': 'joint pain',
        'nausea': 'feeling sick to your stomach',
        'emesis': 'vomiting',
        'diarrhea': 'loose or watery stools',
        'constipation': 'difficulty passing stools',
        'anemia': 'low red blood cell count',
        'leukocytosis': 'high white blood cell count',
        'thrombocytopenia': 'low platelet count',
        'hyperglycemia': 'high blood sugar',
        'hypoglycemia': 'low blood sugar',
        'dyslipidemia': 'abnormal cholesterol levels',
        'hepatomegaly': 'enlarged liver',
        'splenomegaly': 'enlarged spleen',
        'nephropathy': 'kidney disease',
        'neuropathy': 'nerve damage',
        'retinopathy': 'eye damage',
        'cardiomyopathy': 'heart muscle disease',
        'arrhythmia': 'irregular heartbeat',
        'ischemia': 'reduced blood flow',
        'infarction': 'tissue death from lack of blood',
        'stenosis': 'narrowing',
        'occlusion': 'blockage',
        'thrombosis': 'blood clot',
        'embolism': 'traveling blood clot',
        'hemorrhage': 'bleeding',
        'hematoma': 'collection of blood',
        'contusion': 'bruise',
        'laceration': 'cut',
        'abrasion': 'scrape',
        'fracture': 'broken bone',
        'dislocation': 'joint out of place',
        'inflammation': 'swelling and redness',
        'infection': 'invasion by germs',
        'malignancy': 'cancer',
        'benign': 'not cancerous',
        'metastasis': 'cancer spread',
        'remission': 'cancer under control',
        'prognosis': 'expected outcome',
        'diagnosis': 'identification of disease',
        'etiology': 'cause of disease',
        'pathology': 'study of disease',
        'prophylaxis': 'prevention',
        'therapeutic': 'treatment-related',
        'palliative': 'symptom relief',
        'acute': 'sudden and severe',
        'chronic': 'long-lasting',
        'idiopathic': 'unknown cause',
        'congenital': 'present from birth',
        'hereditary': 'passed from parents',
        'acquired': 'developed after birth',
        'systemic': 'affecting whole body',
        'localized': 'in one area',
        'bilateral': 'on both sides',
        'unilateral': 'on one side',
        'proximal': 'closer to center',
        'distal': 'farther from center',
        'anterior': 'front',
        'posterior': 'back',
        'superior': 'upper',
        'inferior': 'lower',
        'medial': 'toward middle',
        'lateral': 'toward side',
    }
    
    @staticmethod
    def simplify_medical_text(text: str) -> str:
        """
        Simplify medical terminology in text
        
        Args:
            text: Text with medical terms
        
        Returns:
            Simplified text
        """
        simplified = text
        
        # Replace medical terms with simple explanations
        for medical_term, simple_term in MedicalNLPService.MEDICAL_TERMS.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(medical_term), re.IGNORECASE)
            simplified = pattern.sub(simple_term, simplified)
        
        return simplified
    
    @staticmethod
    def calculate_readability(text: str) -> Dict[str, float]:
        """
        Calculate readability scores for text
        
        Args:
            text: Text to analyze
        
        Returns:
            Dict with readability scores
        """
        try:
            # Flesch Reading Ease (0-100, higher is easier)
            flesch_reading_ease = textstat.flesch_reading_ease(text)
            
            # Flesch-Kincaid Grade Level (US grade level)
            flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
            
            # SMOG Index (years of education needed)
            smog_index = textstat.smog_index(text)
            
            # Coleman-Liau Index (US grade level)
            coleman_liau = textstat.coleman_liau_index(text)
            
            # Automated Readability Index
            ari = textstat.automated_readability_index(text)
            
            # Average grade level
            avg_grade = (flesch_kincaid_grade + smog_index + coleman_liau + ari) / 4
            
            return {
                'flesch_reading_ease': round(flesch_reading_ease, 2),
                'flesch_kincaid_grade': round(flesch_kincaid_grade, 2),
                'smog_index': round(smog_index, 2),
                'coleman_liau_index': round(coleman_liau, 2),
                'automated_readability_index': round(ari, 2),
                'average_grade_level': round(avg_grade, 2),
                'is_easy_to_read': flesch_reading_ease >= 60,  # 60+ is considered easy
                'readability_level': MedicalNLPService._get_readability_level(flesch_reading_ease)
            }
        except Exception as e:
            return {
                'error': f"Error calculating readability: {str(e)}",
                'is_easy_to_read': None,
                'readability_level': 'unknown'
            }
    
    @staticmethod
    def _get_readability_level(flesch_score: float) -> str:
        """
        Get readability level description from Flesch score
        
        Args:
            flesch_score: Flesch Reading Ease score
        
        Returns:
            Readability level description
        """
        if flesch_score >= 90:
            return 'very easy (5th grade)'
        elif flesch_score >= 80:
            return 'easy (6th grade)'
        elif flesch_score >= 70:
            return 'fairly easy (7th grade)'
        elif flesch_score >= 60:
            return 'standard (8th-9th grade)'
        elif flesch_score >= 50:
            return 'fairly difficult (10th-12th grade)'
        elif flesch_score >= 30:
            return 'difficult (college)'
        else:
            return 'very difficult (college graduate)'
    
    @staticmethod
    def extract_medical_terms(text: str) -> List[Tuple[str, str]]:
        """
        Extract medical terms from text and provide definitions
        
        Args:
            text: Text to analyze
        
        Returns:
            List of (term, definition) tuples
        """
        found_terms = []
        text_lower = text.lower()
        
        for medical_term, simple_term in MedicalNLPService.MEDICAL_TERMS.items():
            if medical_term in text_lower:
                found_terms.append((medical_term, simple_term))
        
        return found_terms
    
    @staticmethod
    def add_term_definitions(text: str) -> str:
        """
        Add definitions for medical terms in text
        
        Args:
            text: Text with medical terms
        
        Returns:
            Text with inline definitions
        """
        result = text
        terms_found = MedicalNLPService.extract_medical_terms(text)
        
        # Add definitions at the end
        if terms_found:
            result += "\n\n**Medical Terms Explained:**\n"
            for term, definition in terms_found:
                result += f"- **{term.title()}**: {definition}\n"
        
        return result
    
    @staticmethod
    def improve_readability(text: str, target_grade: int = 8) -> str:
        """
        Attempt to improve text readability
        
        Args:
            text: Original text
            target_grade: Target grade level (default 8th grade)
        
        Returns:
            Improved text
        """
        # Simplify medical terms
        improved = MedicalNLPService.simplify_medical_text(text)
        
        # Break long sentences (simple heuristic)
        improved = improved.replace(', and ', '. ')
        improved = improved.replace('; ', '. ')
        
        # Remove redundant words
        redundant_phrases = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'at this point in time': 'now',
            'for the purpose of': 'to',
            'in the event that': 'if',
            'with regard to': 'about',
            'in spite of the fact that': 'although',
        }
        
        for phrase, replacement in redundant_phrases.items():
            improved = improved.replace(phrase, replacement)
        
        return improved
    
    @staticmethod
    def validate_patient_friendly(text: str) -> Dict[str, any]:
        """
        Validate if text is patient-friendly
        
        Args:
            text: Text to validate
        
        Returns:
            Validation results with suggestions
        """
        readability = MedicalNLPService.calculate_readability(text)
        medical_terms = MedicalNLPService.extract_medical_terms(text)
        
        # Check for issues
        issues = []
        suggestions = []
        
        # Check readability
        if not readability.get('is_easy_to_read'):
            issues.append('Text may be too complex for average readers')
            suggestions.append('Simplify sentences and use common words')
        
        # Check for unexplained medical terms
        if len(medical_terms) > 3:
            issues.append(f'Contains {len(medical_terms)} medical terms')
            suggestions.append('Consider simplifying or explaining medical terms')
        
        # Check sentence length
        sentences = text.split('.')
        long_sentences = [s for s in sentences if len(s.split()) > 20]
        if len(long_sentences) > len(sentences) / 2:
            issues.append('Many sentences are too long')
            suggestions.append('Break long sentences into shorter ones')
        
        return {
            'is_patient_friendly': len(issues) == 0,
            'readability_score': readability.get('flesch_reading_ease'),
            'grade_level': readability.get('average_grade_level'),
            'medical_terms_count': len(medical_terms),
            'issues': issues,
            'suggestions': suggestions,
            'medical_terms': medical_terms
        }
