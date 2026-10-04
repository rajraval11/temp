import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'temperature.db')
ML_DIR = os.path.join(BASE_DIR, 'ml')
MODEL_PATH = os.path.join(ML_DIR, 'model.pkl')

# Change this to your Arduino's COM port when using hardware mode
ARDUINO_PORT = os.environ.get("ARDUINO_PORT", "COM3")
BAUD_RATE = 9600

# Temperature Thresholds
NORMAL_LIMIT = 35.0
WARNING_LIMIT = 40.0
HIGH_RISK_LIMIT = 40.0 # Everything >= 40 is high risk

SIMULATION_INTERVAL = 2 # seconds
