import sqlite3
import os
import pandas as pd
from config import DB_PATH, DATA_DIR

def get_db_connection():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS temperature_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            source TEXT,
            prediction REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_reading(temperature, source, prediction=None, status="NORMAL"):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO temperature_data (temperature, source, prediction, status)
        VALUES (?, ?, ?, ?)
    ''', (temperature, source, prediction, status))
    inserted_id = c.lastrowid
    conn.commit()
    
    c.execute('SELECT * FROM temperature_data WHERE id = ?', (inserted_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_latest_readings(limit=50):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM temperature_data 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows][::-1]

def get_all_readings_df():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM temperature_data ORDER BY timestamp ASC', conn)
    conn.close()
    return df

def get_analytics():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*), AVG(temperature), MIN(temperature), MAX(temperature) FROM temperature_data')
    row = c.fetchone()
    count, avg_t, min_t, max_t = row if row and row[0] > 0 else (0, 0, 0, 0)
    
    c.execute("SELECT COUNT(*) FROM temperature_data WHERE status='WARNING'")
    warnings = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM temperature_data WHERE status='HIGH RISK'")
    high_risks = c.fetchone()[0]
    
    c.execute("SELECT AVG(prediction), MAX(prediction) FROM temperature_data WHERE prediction IS NOT NULL")
    pred_row = c.fetchone()
    avg_p, max_p = pred_row if pred_row and pred_row[0] is not None else (0, 0)
    
    conn.close()
    return {
        "count": count,
        "avg_temperature": round(avg_t or 0, 2),
        "min_temperature": round(min_t or 0, 2),
        "max_temperature": round(max_t or 0, 2),
        "warnings": warnings,
        "high_risks": high_risks,
        "avg_prediction": round(avg_p or 0, 2),
        "max_prediction": round(max_p or 0, 2)
    }

def get_alerts():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM temperature_data WHERE status != 'NORMAL' ORDER BY timestamp DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
