"""Initialize MongoDB collections with schemas and indexes"""
from .connection import get_mongodb
from .schemas import (
    MEDICAL_KNOWLEDGE_SCHEMA,
    SYMPTOM_DATABASE_SCHEMA,
    TREATMENT_GUIDELINES_SCHEMA,
    LAB_TEST_STANDARDS_SCHEMA
)
import logging

logger = logging.getLogger(__name__)


def create_collection_with_validation(db, collection_name, schema):
    """Create collection with validation schema"""
    try:
        # Check if collection exists
        if collection_name in db.list_collection_names():
            logger.info(f"Collection '{collection_name}' already exists")
            # Update validation schema
            db.command({
                'collMod': collection_name,
                'validator': {'$jsonSchema': schema}
            })
            logger.info(f"Updated validation schema for '{collection_name}'")
        else:
            # Create collection with validation
            db.create_collection(
                collection_name,
                validator={'$jsonSchema': schema}
            )
            logger.info(f"Created collection '{collection_name}' with validation")
    except Exception as e:
        logger.error(f"Error creating collection '{collection_name}': {e}")
        raise


def create_indexes(db):
    """Create indexes for all collections"""
    try:
        # Medical Knowledge Base indexes
        db.medical_knowledge.create_index('disease_name', unique=True)
        db.medical_knowledge.create_index('category')
        db.medical_knowledge.create_index('icd_code')
        db.medical_knowledge.create_index([('disease_name', 'text'), ('description', 'text')])
        logger.info("Created indexes for medical_knowledge collection")
        
        # Symptom Database indexes
        db.symptoms.create_index('symptom_name', unique=True)
        db.symptoms.create_index('category')
        db.symptoms.create_index([('symptom_name', 'text'), ('synonyms', 'text')])
        logger.info("Created indexes for symptoms collection")
        
        # Treatment Guidelines indexes
        db.treatment_guidelines.create_index('condition')
        db.treatment_guidelines.create_index('guideline_source')
        db.treatment_guidelines.create_index('publication_date')
        logger.info("Created indexes for treatment_guidelines collection")
        
        # Lab Test Standards indexes
        db.lab_test_standards.create_index('test_name', unique=True)
        db.lab_test_standards.create_index('test_code')
        db.lab_test_standards.create_index('category')
        logger.info("Created indexes for lab_test_standards collection")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


def initialize_mongodb():
    """Initialize all MongoDB collections"""
    try:
        db = get_mongodb()
        
        logger.info("Initializing MongoDB collections...")
        
        # Create collections with validation
        create_collection_with_validation(db, 'medical_knowledge', MEDICAL_KNOWLEDGE_SCHEMA)
        create_collection_with_validation(db, 'symptoms', SYMPTOM_DATABASE_SCHEMA)
        create_collection_with_validation(db, 'treatment_guidelines', TREATMENT_GUIDELINES_SCHEMA)
        create_collection_with_validation(db, 'lab_test_standards', LAB_TEST_STANDARDS_SCHEMA)
        
        # Create indexes
        create_indexes(db)
        
        logger.info("MongoDB initialization completed successfully")
        
    except Exception as e:
        logger.error(f"MongoDB initialization failed: {e}")
        raise


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize MongoDB
    initialize_mongodb()
