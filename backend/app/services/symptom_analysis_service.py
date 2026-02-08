"""
Symptom Analysis Service with TensorFlow prediction model
"""
import numpy as np
import tensorflow as tf
from typing import List, Dict, Optional, Tuple
import os
import json
from ..mongodb.connection import get_mongodb


class SymptomAnalysisService:
    """Service for symptom analysis and disease prediction"""
    
    def __init__(self):
        """Initialize the service and load/create model"""
        self.model = None
        self.symptom_to_index = {}
        self.index_to_disease = {}
        self.disease_to_index = {}
        self.model_path = 'models/symptom_predictor.h5'
        self.mappings_path = 'models/symptom_mappings.json'
        
        # Try to load existing model, otherwise prepare for training
        self._load_or_prepare_model()
    
    def _load_or_prepare_model(self):
        """Load existing model or prepare data for training"""
        if os.path.exists(self.model_path) and os.path.exists(self.mappings_path):
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                with open(self.mappings_path, 'r') as f:
                    mappings = json.load(f)
                    self.symptom_to_index = mappings['symptom_to_index']
                    self.index_to_disease = {int(k): v for k, v in mappings['index_to_disease'].items()}
                    self.disease_to_index = mappings['disease_to_index']
                print("Loaded existing symptom prediction model")
            except Exception as e:
                print(f"Error loading model: {e}")
                self._prepare_training_data()
        else:
            self._prepare_training_data()
    
    def _prepare_training_data(self):
        """Prepare training data from MongoDB"""
        print("Preparing symptom prediction model...")
        
        # Get data from MongoDB
        db = get_mongodb()
        symptoms_collection = db['symptom_database']
        diseases_collection = db['medical_knowledge']
        
        # Build symptom vocabulary
        all_symptoms = list(symptoms_collection.find())
        symptom_names = [s['name'].lower() for s in all_symptoms]
        self.symptom_to_index = {symptom: idx for idx, symptom in enumerate(symptom_names)}
        
        # Build disease vocabulary
        all_diseases = list(diseases_collection.find())
        disease_names = [d['name'] for d in all_diseases]
        self.disease_to_index = {disease: idx for idx, disease in enumerate(disease_names)}
        self.index_to_disease = {idx: disease for disease, idx in self.disease_to_index.items()}
        
        # Create training data from symptom-disease correlations
        X_train = []
        y_train = []
        
        for symptom_doc in all_symptoms:
            symptom_name = symptom_doc['name'].lower()
            common_diseases = symptom_doc.get('common_diseases', [])
            
            for disease in common_diseases:
                if disease in self.disease_to_index:
                    # Create feature vector (one-hot for this symptom)
                    features = np.zeros(len(self.symptom_to_index))
                    features[self.symptom_to_index[symptom_name]] = 1.0
                    
                    X_train.append(features)
                    y_train.append(self.disease_to_index[disease])
        
        # Also create combinations from disease symptoms
        for disease_doc in all_diseases:
            disease_name = disease_doc['name']
            symptoms = disease_doc.get('symptoms', [])
            
            if disease_name in self.disease_to_index:
                # Create feature vector for all symptoms of this disease
                features = np.zeros(len(self.symptom_to_index))
                for symptom in symptoms:
                    symptom_lower = symptom.lower()
                    if symptom_lower in self.symptom_to_index:
                        features[self.symptom_to_index[symptom_lower]] = 1.0
                
                if features.sum() > 0:  # Only add if we have at least one symptom
                    X_train.append(features)
                    y_train.append(self.disease_to_index[disease_name])
        
        if len(X_train) > 0:
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            
            # Train the model
            self._train_model(X_train, y_train)
        else:
            print("Warning: No training data available. Using rule-based fallback.")
            self.model = None
    
    def _train_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train TensorFlow neural network model
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        print(f"Training model with {len(X_train)} samples...")
        
        input_dim = X_train.shape[1]
        num_classes = len(self.disease_to_index)
        
        # Build neural network (input layer, 3 hidden layers, output layer)
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        self.model = model
        
        # Save model and mappings
        os.makedirs('models', exist_ok=True)
        model.save(self.model_path)
        
        mappings = {
            'symptom_to_index': self.symptom_to_index,
            'index_to_disease': self.index_to_disease,
            'disease_to_index': self.disease_to_index
        }
        
        with open(self.mappings_path, 'w') as f:
            json.dump(mappings, f)
        
        print("Model trained and saved successfully")
    
    def analyze_symptoms(
        self,
        symptoms: List[str],
        age: Optional[int] = None,
        gender: Optional[str] = None
    ) -> Dict:
        """
        Analyze symptoms and predict possible diseases
        
        Args:
            symptoms: List of symptom names
            age: Optional patient age
            gender: Optional patient gender
        
        Returns:
            Dict with predictions and metadata
        """
        # Normalize symptoms
        symptoms_lower = [s.lower().strip() for s in symptoms]
        
        # If model is available, use it
        if self.model is not None:
            return self._predict_with_model(symptoms_lower)
        else:
            # Fallback to rule-based approach
            return self._predict_rule_based(symptoms_lower)
    
    def _predict_with_model(self, symptoms: List[str]) -> Dict:
        """
        Predict using TensorFlow model
        
        Args:
            symptoms: List of symptom names (lowercase)
        
        Returns:
            Predictions dict
        """
        # Create feature vector
        features = np.zeros(len(self.symptom_to_index))
        
        for symptom in symptoms:
            if symptom in self.symptom_to_index:
                features[self.symptom_to_index[symptom]] = 1.0
        
        # Reshape for model input
        features = features.reshape(1, -1)
        
        # Get predictions
        predictions = self.model.predict(features, verbose=0)[0]
        
        # Get top predictions with confidence >= 0.6
        top_indices = np.argsort(predictions)[::-1]
        
        results = []
        for idx in top_indices:
            confidence = float(predictions[idx])
            if confidence >= 0.6 and len(results) < 3:  # Top 3 with confidence >= 0.6
                disease_name = self.index_to_disease[idx]
                results.append({
                    'disease': disease_name,
                    'confidence': round(confidence, 3)
                })
        
        # If no predictions meet threshold, return top 3 anyway
        if len(results) == 0:
            for idx in top_indices[:3]:
                disease_name = self.index_to_disease[idx]
                confidence = float(predictions[idx])
                results.append({
                    'disease': disease_name,
                    'confidence': round(confidence, 3)
                })
        
        avg_confidence = np.mean([r['confidence'] for r in results]) if results else 0.0
        
        return {
            'predictions': results,
            'method': 'tensorflow_model',
            'avg_confidence': round(avg_confidence, 3)
        }
    
    def _predict_rule_based(self, symptoms: List[str]) -> Dict:
        """
        Fallback rule-based prediction using MongoDB correlations
        
        Args:
            symptoms: List of symptom names (lowercase)
        
        Returns:
            Predictions dict
        """
        db = get_mongodb()
        symptoms_collection = db['symptom_database']
        
        # Count disease occurrences across symptoms
        disease_scores = {}
        
        for symptom in symptoms:
            symptom_doc = symptoms_collection.find_one(
                {'name': {'$regex': f'^{symptom}$', '$options': 'i'}}
            )
            
            if symptom_doc and 'common_diseases' in symptom_doc:
                for disease in symptom_doc['common_diseases']:
                    disease_scores[disease] = disease_scores.get(disease, 0) + 1
        
        # Calculate confidence scores (normalized by number of symptoms)
        total_symptoms = len(symptoms)
        results = []
        
        for disease, score in sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)[:3]:
            confidence = score / total_symptoms
            if confidence >= 0.6 or len(results) < 3:
                results.append({
                    'disease': disease,
                    'confidence': round(confidence, 3)
                })
        
        avg_confidence = np.mean([r['confidence'] for r in results]) if results else 0.0
        
        return {
            'predictions': results,
            'method': 'rule_based',
            'avg_confidence': round(avg_confidence, 3)
        }
    
    def calculate_risk_severity(self, predictions: List[Dict]) -> str:
        """
        Calculate risk severity from predictions
        
        Args:
            predictions: List of prediction dicts with confidence scores
        
        Returns:
            Risk level: 'low', 'medium', 'high', or 'critical'
        """
        if not predictions:
            return 'low'
        
        # Get highest confidence
        max_confidence = max(p['confidence'] for p in predictions)
        
        # Check for critical diseases
        critical_diseases = ['heart attack', 'stroke', 'sepsis', 'meningitis']
        for pred in predictions:
            if any(critical in pred['disease'].lower() for critical in critical_diseases):
                return 'critical'
        
        # Assign risk based on confidence
        if max_confidence >= 0.9:
            return 'high'
        elif max_confidence >= 0.75:
            return 'medium'
        else:
            return 'low'
    
    def format_analysis_results(
        self,
        predictions: List[Dict],
        risk_severity: str,
        symptoms: List[str]
    ) -> Dict:
        """
        Format symptom analysis results with recommendations
        
        Args:
            predictions: List of predictions
            risk_severity: Risk severity level
            symptoms: Original symptoms
        
        Returns:
            Formatted results dict
        """
        # Get disease details from MongoDB
        db = get_mongodb()
        diseases_collection = db['medical_knowledge']
        
        formatted_predictions = []
        for pred in predictions[:3]:  # Top 3
            disease_doc = diseases_collection.find_one(
                {'name': {'$regex': f'^{pred["disease"]}$', '$options': 'i'}}
            )
            
            if disease_doc:
                formatted_predictions.append({
                    'disease': pred['disease'],
                    'confidence': pred['confidence'],
                    'description': disease_doc.get('description', 'No description available'),
                    'treatment_options': disease_doc.get('treatment_options', [])[:3],
                    'when_to_see_doctor': disease_doc.get('when_to_see_doctor', 'Consult a healthcare provider')
                })
            else:
                formatted_predictions.append({
                    'disease': pred['disease'],
                    'confidence': pred['confidence'],
                    'description': 'No additional information available',
                    'treatment_options': [],
                    'when_to_see_doctor': 'Consult a healthcare provider for proper diagnosis'
                })
        
        # Generate recommendations based on risk
        recommendations = self._get_recommendations(risk_severity, symptoms)
        
        # Medical disclaimer
        disclaimer = ("⚕️ **Important Medical Disclaimer**: This analysis is for informational purposes only "
                     "and does not constitute medical advice, diagnosis, or treatment. The predictions are based "
                     "on statistical patterns and may not be accurate for your specific situation. Always consult "
                     "with a qualified healthcare professional for proper medical evaluation and diagnosis.")
        
        return {
            'predictions': formatted_predictions,
            'recommendations': recommendations,
            'disclaimer': disclaimer
        }
    
    def _get_recommendations(self, risk_severity: str, symptoms: List[str]) -> List[str]:
        """
        Get recommendations based on risk severity
        
        Args:
            risk_severity: Risk level
            symptoms: List of symptoms
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if risk_severity == 'critical':
            recommendations.append("🚨 Seek immediate medical attention or call emergency services (911)")
            recommendations.append("Do not wait - this could be a medical emergency")
            recommendations.append("Go to the nearest emergency room if safe to do so")
        elif risk_severity == 'high':
            recommendations.append("⚠️ Schedule an appointment with your doctor as soon as possible")
            recommendations.append("Monitor your symptoms closely")
            recommendations.append("Seek immediate care if symptoms worsen")
        elif risk_severity == 'medium':
            recommendations.append("📋 Consider scheduling a doctor's appointment within the next few days")
            recommendations.append("Keep track of your symptoms and any changes")
            recommendations.append("Rest and stay hydrated")
        else:  # low
            recommendations.append("✓ Monitor your symptoms over the next few days")
            recommendations.append("Get adequate rest and maintain good hydration")
            recommendations.append("Contact your doctor if symptoms persist or worsen")
        
        # Add general recommendations
        recommendations.append("Keep a symptom diary to share with your healthcare provider")
        
        return recommendations
