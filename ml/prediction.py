import os
import joblib
from ml.feature_engineering import prepare_latest_features
from config import MODEL_PATH, NORMAL_LIMIT, WARNING_LIMIT, HIGH_RISK_LIMIT
from backend.database import get_latest_readings

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def predict_next_temperature(current_temp):
    model = load_model()
    if not model:
        return None
        
    latest = get_latest_readings(limit=4)
    recent_temps = [r['temperature'] for r in latest]
    
    if not recent_temps or recent_temps[-1] != current_temp:
        recent_temps.append(current_temp)
        
    features = prepare_latest_features(recent_temps)
    if features is None:
        return None
        
    feature_cols = [
        'temperature_t', 
        'temperature_t_minus_1', 
        'temperature_t_minus_2', 
        'temperature_t_minus_3',
        'rolling_mean', 
        'temperature_change',
        'temperature_change_previous',
        'trend'
    ]
    prediction = model.predict(features[feature_cols])[0]
    return round(prediction, 2)

def determine_status(temperature, predicted_temp=None):
    temp_to_check = predicted_temp if predicted_temp is not None else temperature
    
    if temp_to_check < NORMAL_LIMIT:
        return "NORMAL"
    elif temp_to_check < WARNING_LIMIT:
        return "WARNING"
    else:
        return "HIGH RISK"
