"""Seed MongoDB with initial medical knowledge data"""
from datetime import datetime
from .repositories import (
    MedicalKnowledgeRepository,
    SymptomRepository,
    TreatmentGuidelineRepository,
    LabTestStandardRepository
)
import logging

logger = logging.getLogger(__name__)


# Sample medical knowledge data
SAMPLE_DISEASES = [
    {
        "disease_name": "Common Cold",
        "icd_code": "J00",
        "category": "Respiratory",
        "description": "A viral infection of the upper respiratory tract, primarily affecting the nose and throat.",
        "simple_explanation": "The common cold is a viral infection that makes your nose stuffy and throat sore. It usually goes away on its own in about a week.",
        "symptoms": ["runny nose", "sore throat", "cough", "sneezing", "mild headache", "fatigue"],
        "causes": ["Rhinovirus", "Coronavirus", "Respiratory syncytial virus"],
        "risk_factors": ["Weakened immune system", "Close contact with infected individuals", "Touching contaminated surfaces"],
        "complications": ["Sinus infection", "Ear infection", "Bronchitis"],
        "prevention": ["Frequent handwashing", "Avoiding close contact with sick people", "Not touching face with unwashed hands"],
        "treatment_options": [
            {
                "type": "Self-care",
                "description": "Rest, hydration, and over-the-counter medications",
                "medications": ["Acetaminophen", "Ibuprofen", "Decongestants"]
            }
        ],
        "lifestyle_recommendations": ["Get plenty of rest", "Drink lots of fluids", "Use a humidifier"],
        "when_to_see_doctor": ["Symptoms last more than 10 days", "High fever above 101.3°F", "Difficulty breathing"],
        "related_conditions": ["Influenza", "Sinusitis", "Bronchitis"],
        "references": ["CDC Common Cold Guidelines", "Mayo Clinic"],
        "last_updated": datetime.utcnow()
    },
    {
        "disease_name": "Type 2 Diabetes",
        "icd_code": "E11",
        "category": "Endocrine",
        "description": "A chronic condition affecting how the body processes blood sugar (glucose).",
        "simple_explanation": "Type 2 diabetes means your body doesn't use insulin properly, causing high blood sugar levels. It can be managed with lifestyle changes and medication.",
        "symptoms": ["increased thirst", "frequent urination", "increased hunger", "fatigue", "blurred vision", "slow healing wounds"],
        "causes": ["Insulin resistance", "Insufficient insulin production"],
        "risk_factors": ["Obesity", "Sedentary lifestyle", "Family history", "Age over 45"],
        "complications": ["Heart disease", "Kidney damage", "Nerve damage", "Eye damage"],
        "prevention": ["Maintain healthy weight", "Regular physical activity", "Healthy diet"],
        "treatment_options": [
            {
                "type": "Medication",
                "description": "Oral medications and insulin therapy",
                "medications": ["Metformin", "Sulfonylureas", "DPP-4 inhibitors"]
            },
            {
                "type": "Lifestyle",
                "description": "Diet and exercise modifications",
                "medications": []
            }
        ],
        "lifestyle_recommendations": ["Eat a balanced diet", "Exercise regularly", "Monitor blood sugar", "Maintain healthy weight"],
        "when_to_see_doctor": ["Blood sugar consistently high", "Symptoms of complications", "Difficulty managing condition"],
        "related_conditions": ["Prediabetes", "Metabolic syndrome", "Cardiovascular disease"],
        "references": ["American Diabetes Association", "WHO Diabetes Guidelines"],
        "last_updated": datetime.utcnow()
    },
    {
        "disease_name": "Hypertension",
        "icd_code": "I10",
        "category": "Cardiovascular",
        "description": "A condition in which the force of blood against artery walls is consistently too high.",
        "simple_explanation": "High blood pressure means your heart is working harder than normal to pump blood. It often has no symptoms but can lead to serious health problems.",
        "symptoms": ["headaches", "shortness of breath", "nosebleeds"],
        "causes": ["Unknown (primary)", "Kidney disease", "Hormonal disorders"],
        "risk_factors": ["Age", "Family history", "Obesity", "High salt intake", "Lack of exercise"],
        "complications": ["Heart attack", "Stroke", "Heart failure", "Kidney disease"],
        "prevention": ["Healthy diet", "Regular exercise", "Limit alcohol", "Reduce stress"],
        "treatment_options": [
            {
                "type": "Medication",
                "description": "Antihypertensive medications",
                "medications": ["ACE inhibitors", "Beta blockers", "Diuretics", "Calcium channel blockers"]
            }
        ],
        "lifestyle_recommendations": ["Reduce sodium intake", "Exercise 30 minutes daily", "Maintain healthy weight", "Limit alcohol"],
        "when_to_see_doctor": ["Blood pressure consistently above 140/90", "Severe headache", "Chest pain"],
        "related_conditions": ["Coronary artery disease", "Stroke", "Kidney disease"],
        "references": ["American Heart Association", "JNC 8 Guidelines"],
        "last_updated": datetime.utcnow()
    }
]

# Sample symptoms
SAMPLE_SYMPTOMS = [
    {
        "symptom_name": "fever",
        "synonyms": ["high temperature", "pyrexia", "elevated temperature"],
        "category": "General",
        "severity_indicators": ["Temperature above 103°F", "Fever lasting more than 3 days"],
        "associated_diseases": [
            {"disease_id": "Common Cold", "correlation_strength": 0.6},
            {"disease_id": "Influenza", "correlation_strength": 0.9}
        ],
        "questions_to_ask": ["How high is the fever?", "How long have you had it?", "Any other symptoms?"],
        "red_flags": ["Fever above 104°F", "Fever with stiff neck", "Fever with rash"]
    },
    {
        "symptom_name": "cough",
        "synonyms": ["coughing", "hacking"],
        "category": "Respiratory",
        "severity_indicators": ["Coughing up blood", "Persistent cough over 3 weeks"],
        "associated_diseases": [
            {"disease_id": "Common Cold", "correlation_strength": 0.8},
            {"disease_id": "Bronchitis", "correlation_strength": 0.9}
        ],
        "questions_to_ask": ["Is it dry or productive?", "Any blood in sputum?", "How long?"],
        "red_flags": ["Coughing up blood", "Severe shortness of breath", "Chest pain"]
    },
    {
        "symptom_name": "headache",
        "synonyms": ["head pain", "cephalalgia"],
        "category": "Neurological",
        "severity_indicators": ["Sudden severe headache", "Headache with vision changes"],
        "associated_diseases": [
            {"disease_id": "Migraine", "correlation_strength": 0.8},
            {"disease_id": "Hypertension", "correlation_strength": 0.5}
        ],
        "questions_to_ask": ["Where is the pain?", "How severe?", "Any triggers?"],
        "red_flags": ["Worst headache ever", "Headache with fever and stiff neck", "Sudden onset"]
    },
    {
        "symptom_name": "fatigue",
        "synonyms": ["tiredness", "exhaustion", "lethargy"],
        "category": "General",
        "severity_indicators": ["Unable to perform daily activities", "Persistent for weeks"],
        "associated_diseases": [
            {"disease_id": "Type 2 Diabetes", "correlation_strength": 0.7},
            {"disease_id": "Anemia", "correlation_strength": 0.8}
        ],
        "questions_to_ask": ["How long?", "Affecting daily life?", "Any other symptoms?"],
        "red_flags": ["Sudden severe fatigue", "Fatigue with chest pain", "Unexplained weight loss"]
    }
]

# Sample lab test standards
SAMPLE_LAB_TESTS = [
    {
        "test_name": "Glucose (Fasting)",
        "test_code": "GLU",
        "category": "Metabolic",
        "unit": "mg/dL",
        "reference_ranges": [
            {
                "age_group": "Adult",
                "gender": "All",
                "min_value": 70.0,
                "max_value": 100.0,
                "optimal_range": {"min": 70.0, "max": 85.0}
            }
        ],
        "interpretation": {
            "low": "Hypoglycemia - may indicate insulin overdose or other conditions",
            "normal": "Normal glucose metabolism",
            "high": "Hyperglycemia - may indicate diabetes or prediabetes",
            "critical_low": 50.0,
            "critical_high": 400.0
        },
        "clinical_significance": "Measures blood sugar levels to diagnose and monitor diabetes",
        "related_tests": ["HbA1c", "Glucose Tolerance Test"]
    },
    {
        "test_name": "Hemoglobin A1c",
        "test_code": "HBA1C",
        "category": "Metabolic",
        "unit": "%",
        "reference_ranges": [
            {
                "age_group": "Adult",
                "gender": "All",
                "min_value": 4.0,
                "max_value": 5.6,
                "optimal_range": {"min": 4.0, "max": 5.4}
            }
        ],
        "interpretation": {
            "low": "Rare, may indicate anemia or other conditions",
            "normal": "Normal glucose control over past 3 months",
            "high": "Poor glucose control, indicates diabetes or prediabetes",
            "critical_low": 3.0,
            "critical_high": 14.0
        },
        "clinical_significance": "Reflects average blood sugar over past 2-3 months",
        "related_tests": ["Fasting Glucose", "Glucose Tolerance Test"]
    },
    {
        "test_name": "Total Cholesterol",
        "test_code": "CHOL",
        "category": "Lipid Panel",
        "unit": "mg/dL",
        "reference_ranges": [
            {
                "age_group": "Adult",
                "gender": "All",
                "min_value": 0.0,
                "max_value": 200.0,
                "optimal_range": {"min": 125.0, "max": 200.0}
            }
        ],
        "interpretation": {
            "low": "Generally not concerning unless very low",
            "normal": "Desirable cholesterol level",
            "high": "Increased risk of heart disease",
            "critical_low": 0.0,
            "critical_high": 400.0
        },
        "clinical_significance": "Measures total cholesterol to assess cardiovascular risk",
        "related_tests": ["LDL", "HDL", "Triglycerides"]
    }
]

# Sample treatment guidelines
SAMPLE_GUIDELINES = [
    {
        "condition": "Type 2 Diabetes",
        "guideline_source": "American Diabetes Association",
        "publication_date": datetime(2023, 1, 1),
        "recommendations": [
            {
                "stage": "Initial",
                "interventions": ["Lifestyle modification", "Metformin therapy"],
                "medications": [
                    {
                        "name": "Metformin",
                        "dosage": "500-2000mg daily",
                        "duration": "Ongoing",
                        "contraindications": ["Severe kidney disease", "Liver disease"]
                    }
                ],
                "lifestyle_changes": ["Weight loss 5-10%", "150 minutes exercise weekly", "Mediterranean diet"],
                "monitoring": ["HbA1c every 3 months", "Annual eye exam", "Annual foot exam"]
            }
        ],
        "evidence_level": "A",
        "references": ["ADA Standards of Care 2023"]
    }
]


def seed_medical_knowledge():
    """Seed medical knowledge base"""
    repo = MedicalKnowledgeRepository()
    
    logger.info("Seeding medical knowledge base...")
    for disease in SAMPLE_DISEASES:
        try:
            existing = repo.find_by_disease_name(disease['disease_name'])
            if not existing:
                repo.insert_disease(disease)
                logger.info(f"Inserted disease: {disease['disease_name']}")
            else:
                logger.info(f"Disease already exists: {disease['disease_name']}")
        except Exception as e:
            logger.error(f"Error inserting disease {disease['disease_name']}: {e}")


def seed_symptoms():
    """Seed symptom database"""
    repo = SymptomRepository()
    
    logger.info("Seeding symptom database...")
    for symptom in SAMPLE_SYMPTOMS:
        try:
            existing = repo.find_by_name(symptom['symptom_name'])
            if not existing:
                repo.insert_symptom(symptom)
                logger.info(f"Inserted symptom: {symptom['symptom_name']}")
            else:
                logger.info(f"Symptom already exists: {symptom['symptom_name']}")
        except Exception as e:
            logger.error(f"Error inserting symptom {symptom['symptom_name']}: {e}")


def seed_lab_tests():
    """Seed lab test standards"""
    repo = LabTestStandardRepository()
    
    logger.info("Seeding lab test standards...")
    for test in SAMPLE_LAB_TESTS:
        try:
            existing = repo.find_by_test_name(test['test_name'])
            if not existing:
                repo.insert_test_standard(test)
                logger.info(f"Inserted lab test: {test['test_name']}")
            else:
                logger.info(f"Lab test already exists: {test['test_name']}")
        except Exception as e:
            logger.error(f"Error inserting lab test {test['test_name']}: {e}")


def seed_treatment_guidelines():
    """Seed treatment guidelines"""
    repo = TreatmentGuidelineRepository()
    
    logger.info("Seeding treatment guidelines...")
    for guideline in SAMPLE_GUIDELINES:
        try:
            existing = repo.find_latest_by_condition(guideline['condition'])
            if not existing:
                repo.insert_guideline(guideline)
                logger.info(f"Inserted guideline for: {guideline['condition']}")
            else:
                logger.info(f"Guideline already exists for: {guideline['condition']}")
        except Exception as e:
            logger.error(f"Error inserting guideline for {guideline['condition']}: {e}")


def seed_all():
    """Seed all MongoDB collections"""
    try:
        logger.info("Starting MongoDB seeding process...")
        
        seed_medical_knowledge()
        seed_symptoms()
        seed_lab_tests()
        seed_treatment_guidelines()
        
        logger.info("MongoDB seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        raise


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run seeding
    seed_all()
