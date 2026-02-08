# MongoDB Module

This module handles MongoDB connections, schemas, and data access for the medical knowledge base.

## Structure

- `connection.py` - MongoDB connection management
- `schemas.py` - Collection schemas and validation rules
- `init_collections.py` - Collection initialization with indexes
- `repositories.py` - Data access layer (repository pattern)
- `seed_data.py` - Initial data seeding

## Collections

### 1. Medical Knowledge Base
Stores disease information, symptoms, treatments, and patient-friendly explanations.

**Fields:**
- disease_name (unique)
- icd_code
- category
- description
- simple_explanation
- symptoms, causes, risk_factors
- treatment_options
- lifestyle_recommendations
- references

### 2. Symptom Database
Stores symptom information and disease correlations.

**Fields:**
- symptom_name (unique)
- synonyms
- category
- associated_diseases with correlation strengths
- red_flags

### 3. Treatment Guidelines
Stores evidence-based treatment recommendations.

**Fields:**
- condition
- guideline_source
- recommendations by stage
- medications with dosages
- evidence_level

### 4. Lab Test Standards
Stores reference ranges and interpretations for lab tests.

**Fields:**
- test_name (unique)
- test_code
- reference_ranges by age/gender
- interpretation (low, normal, high)
- clinical_significance

## Usage

### Initialize Collections

```python
from app.mongodb import initialize_mongodb

# Create collections with schemas and indexes
initialize_mongodb()
```

### Seed Initial Data

```python
from app.mongodb.seed_data import seed_all

# Populate with sample medical data
seed_all()
```

### Use Repositories

```python
from app.mongodb import MedicalKnowledgeRepository, SymptomRepository

# Medical knowledge
med_repo = MedicalKnowledgeRepository()
disease_info = med_repo.find_by_disease_name("Type 2 Diabetes")

# Symptoms
symptom_repo = SymptomRepository()
symptoms = symptom_repo.search_symptoms("head")  # Returns headache, etc.
```

## Running Setup

```bash
# Initialize collections
python -m app.mongodb.init_collections

# Seed data
python -m app.mongodb.seed_data
```

## Indexes

All collections have appropriate indexes for:
- Unique constraints (disease_name, symptom_name, test_name)
- Text search (full-text search on descriptions)
- Category filtering
- Date sorting

## Validation

MongoDB schema validation ensures data integrity:
- Required fields are enforced
- Data types are validated
- Array structures are validated
