import pandas as pd
import numpy as np

def create_features(df):
    if len(df) < 4:
        return pd.DataFrame()
        
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Target (next temperature)
    df['next_temperature'] = df['temperature'].shift(-1)
    
    # Features
    df['temperature_t'] = df['temperature']
    df['temperature_t_minus_1'] = df['temperature'].shift(1)
    df['temperature_t_minus_2'] = df['temperature'].shift(2)
    df['temperature_t_minus_3'] = df['temperature'].shift(3)
    
    df['rolling_mean'] = df['temperature'].rolling(window=4, min_periods=4).mean()
    df['temperature_change'] = df['temperature_t'] - df['temperature_t_minus_1']
    df['temperature_change_previous'] = df['temperature_t_minus_1'] - df['temperature_t_minus_2']
    
    # trend/slope (using last 3 points)
    df['trend'] = (df['temperature_t'] - df['temperature_t_minus_3']) / 3.0
    
    df = df.dropna(subset=[
        'next_temperature', 
        'temperature_t', 
        'temperature_t_minus_1', 
        'temperature_t_minus_2', 
        'temperature_t_minus_3',
        'rolling_mean', 
        'temperature_change',
        'temperature_change_previous',
        'trend'
    ])
    
    return df

def prepare_latest_features(recent_temps):
    # recent_temps must have at least 4 elements
    if len(recent_temps) < 4:
        return None
        
    t = recent_temps[-1]
    t_minus_1 = recent_temps[-2]
    t_minus_2 = recent_temps[-3]
    t_minus_3 = recent_temps[-4]
    
    rolling_mean = (t + t_minus_1 + t_minus_2 + t_minus_3) / 4.0
    temp_change = t - t_minus_1
    temp_change_prev = t_minus_1 - t_minus_2
    trend = (t - t_minus_3) / 3.0
    
    return pd.DataFrame([{
        'temperature_t': t,
        'temperature_t_minus_1': t_minus_1,
        'temperature_t_minus_2': t_minus_2,
        'temperature_t_minus_3': t_minus_3,
        'rolling_mean': rolling_mean,
        'temperature_change': temp_change,
        'temperature_change_previous': temp_change_prev,
        'trend': trend
    }])
