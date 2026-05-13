import joblib
import pandas as pd
import os
import numpy as np
import warnings
import sys

# Suppress scikit-learn version incompatibility warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Compatibility patch for scikit-learn version mismatch
try:
    from sklearn.compose._column_transformer import _RemainderColsList
except (ImportError, AttributeError):
    # If _RemainderColsList doesn't exist, create a placeholder
    import sklearn.compose._column_transformer as ct
    if not hasattr(ct, '_RemainderColsList'):
        class _RemainderColsList(list):
            """Placeholder for sklearn compatibility"""
            pass
        ct._RemainderColsList = _RemainderColsList

# Load the model once at module initialization
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'panic_disorder_rf_model.joblib')
try:
    # Suppress version incompatibility warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def predict(form_data):
    """
    Args:
        form_data (dict): Dictionary containing form field values
        
    Returns:
        dict: Dictionary with prediction, confidence, and message
    """
    if model is None:
        return {
            'prediction': 'Error',
            'confidence': 0,
            'message': 'Model failed to load. Please try again later.'
        }
    
    try:
        
        df = pd.DataFrame([{
            'Lifestyle Factors': form_data.get('lifestyle', ''), # in get() the second argument is the default value if the key is not found
            'Current Stressors': form_data.get('stressors', ''),
            'Symptoms': form_data.get('symptoms', ''),
            'Severity': form_data.get('severity', ''),
            'Impact on Life': form_data.get('impact', ''),
            'Age': float(form_data.get('age', 0)),
            'Coping Mechanisms': form_data.get('coping_mechanisms', ''),
            'Family History': form_data.get('family_history', ''),
            'Social Support': form_data.get('social_support', ''),
            'Personal History': form_data.get('personal_history', ''),
        }])
        
        # Make prediction
        prediction = model.predict(df)[0]
        
        # Get prediction probabilities for confidence
        probabilities = model.predict_proba(df)[0]
        confidence = np.max(probabilities)
        
        # Map prediction to label
        prediction_label = 'Positive' if prediction == 1 else 'Negative'
        
        # Generate appropriate message
        if prediction == 1:
            message = f'Based on your assessment, you show signs of panic disorder (Confidence: {confidence*100:.1f}%). We recommend consulting with a mental health professional for proper evaluation and treatment.'
        else:
            message = f'Based on your assessment, you do not show significant signs of panic disorder (Confidence: {confidence*100:.1f}%). However, if you have concerns about your mental health, please consult a healthcare professional.'
        
        return {
            'prediction': prediction_label,
            'confidence': confidence,
            'message': message
        }
    
    except Exception as e:
        return {
            'prediction': 'Error',
            'confidence': 0,
            'message': f'An error occurred during prediction: {str(e)}'
        }