import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from ml.feature_engineering import create_features
from config import MODEL_PATH, ML_DIR
from backend.database import get_all_readings_df

def train_and_save_model():
    df = get_all_readings_df()
    if len(df) < 20:
        return False, "Not enough data to train model (need at least 20 readings)."
    
    df_features = create_features(df)
    
    if len(df_features) < 10:
        return False, "Not enough featured data to train model."
        
    features = [
        'temperature_t', 
        'temperature_t_minus_1', 
        'temperature_t_minus_2', 
        'temperature_t_minus_3',
        'rolling_mean', 
        'temperature_change',
        'temperature_change_previous',
        'trend'
    ]
    
    X = df_features[features]
    y = df_features['next_temperature']
    
    # Chronological train/test split (80/20)
    split_idx = int(len(df_features) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    mae, rmse, r2 = 0.0, 0.0, 0.0
    if len(X_test) > 0:
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        print(f"Model evaluated. MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.2f}")
    
    # Retrain on full data for actual use
    model.fit(X, y)
    
    if not os.path.exists(ML_DIR):
        os.makedirs(ML_DIR)
        
    joblib.dump(model, MODEL_PATH)
    
    msg = f"Model trained successfully. MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.2f}" if len(X_test) > 0 else "Model trained."
    return True, msg
