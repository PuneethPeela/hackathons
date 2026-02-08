"""MongoDB collection schemas and validation"""

# Medical Knowledge Base Schema
MEDICAL_KNOWLEDGE_SCHEMA = {
    "bsonType": "object",
    "required": ["disease_name", "category", "description", "simple_explanation"],
    "properties": {
        "disease_name": {
            "bsonType": "string",
            "description": "Name of the disease"
        },
        "icd_code": {
            "bsonType": "string",
            "description": "ICD-10 code"
        },
        "category": {
            "bsonType": "string",
            "description": "Disease category"
        },
        "description": {
            "bsonType": "string",
            "description": "Medical description"
        },
        "simple_explanation": {
            "bsonType": "string",
            "description": "Patient-friendly explanation"
        },
        "symptoms": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "causes": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "risk_factors": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "complications": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "prevention": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "treatment_options": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "properties": {
                    "type": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "medications": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    }
                }
            }
        },
        "lifestyle_recommendations": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "when_to_see_doctor": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "related_conditions": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "references": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "last_updated": {
            "bsonType": "date"
        }
    }
}

# Symptom Database Schema
SYMPTOM_DATABASE_SCHEMA = {
    "bsonType": "object",
    "required": ["symptom_name", "category"],
    "properties": {
        "symptom_name": {
            "bsonType": "string",
            "description": "Name of the symptom"
        },
        "synonyms": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "category": {
            "bsonType": "string",
            "description": "Symptom category"
        },
        "severity_indicators": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "associated_diseases": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "properties": {
                    "disease_id": {"bsonType": "string"},
                    "correlation_strength": {"bsonType": "double"}
                }
            }
        },
        "questions_to_ask": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        },
        "red_flags": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        }
    }
}

# Treatment Guidelines Schema
TREATMENT_GUIDELINES_SCHEMA = {
    "bsonType": "object",
    "required": ["condition", "guideline_source"],
    "properties": {
        "condition": {
            "bsonType": "string",
            "description": "Medical condition"
        },
        "guideline_source": {
            "bsonType": "string",
            "description": "Source of guidelines"
        },
        "publication_date": {
            "bsonType": "date"
        },
        "recommendations": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "properties": {
                    "stage": {"bsonType": "string"},
                    "interventions": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "medications": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "name": {"bsonType": "string"},
                                "dosage": {"bsonType": "string"},
                                "duration": {"bsonType": "string"},
                                "contraindications": {
                                    "bsonType": "array",
                                    "items": {"bsonType": "string"}
                                }
                            }
                        }
                    },
                    "lifestyle_changes": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "monitoring": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    }
                }
            }
        },
        "evidence_level": {
            "bsonType": "string"
        },
        "references": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        }
    }
}

# Lab Test Standards Schema
LAB_TEST_STANDARDS_SCHEMA = {
    "bsonType": "object",
    "required": ["test_name", "category", "unit"],
    "properties": {
        "test_name": {
            "bsonType": "string",
            "description": "Name of the lab test"
        },
        "test_code": {
            "bsonType": "string"
        },
        "category": {
            "bsonType": "string"
        },
        "unit": {
            "bsonType": "string"
        },
        "reference_ranges": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "properties": {
                    "age_group": {"bsonType": "string"},
                    "gender": {"bsonType": "string"},
                    "min_value": {"bsonType": "double"},
                    "max_value": {"bsonType": "double"},
                    "optimal_range": {
                        "bsonType": "object",
                        "properties": {
                            "min": {"bsonType": "double"},
                            "max": {"bsonType": "double"}
                        }
                    }
                }
            }
        },
        "interpretation": {
            "bsonType": "object",
            "properties": {
                "low": {"bsonType": "string"},
                "normal": {"bsonType": "string"},
                "high": {"bsonType": "string"},
                "critical_low": {"bsonType": "double"},
                "critical_high": {"bsonType": "double"}
            }
        },
        "clinical_significance": {
            "bsonType": "string"
        },
        "related_tests": {
            "bsonType": "array",
            "items": {"bsonType": "string"}
        }
    }
}
