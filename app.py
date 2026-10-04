import os
from flask import Flask
from flask_cors import CORS
from backend.database import init_db, insert_reading
from ml.train_model import train_and_save_model
import config
from backend.routes import api
from backend.simulator import TemperatureSimulator
from backend.serial_reader import SerialReader

app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='/static')
CORS(app)

app.register_blueprint(api)

def generate_initial_data():
    from backend.database import get_latest_readings, insert_reading
    import random
    
    if len(get_latest_readings(1)) == 0:
        print("Generating initial training data...")
        sequences = []
        
        # NORMAL variations (20 - 35)
        for start_temp in [20, 25, 30]:
            t = start_temp
            for _ in range(60):
                t += random.uniform(-0.8, 0.8)
                t = max(20, min(35, t))
                sequences.append(t)
                
        # INCREASING (25 - 45)
        t = 25.0
        for _ in range(50):
            t += random.uniform(0.1, 0.7)
            sequences.append(t)
            
        # STRONG INCREASE (30 - 55)
        t = 30.0
        for _ in range(30):
            t += random.uniform(0.5, 1.5)
            sequences.append(t)
            
        # EXTREME OVERHEATING (40 - 60)
        t = 40.0
        for _ in range(20):
            t += random.uniform(0.8, 2.0)
            sequences.append(t)
            
        # DECREASING (55 - 25)
        t = 55.0
        for _ in range(40):
            t -= random.uniform(0.2, 1.2)
            sequences.append(t)
            
        # RANDOM REALISTIC
        t = 28.0
        for _ in range(60):
            t += random.uniform(-1.5, 1.5)
            t = max(15, min(65, t))
            sequences.append(t)
            
        for temp in sequences:
            insert_reading(round(temp, 2), "simulation", prediction=None, status="NORMAL")
            
        print(f"Generated {len(sequences)} initial data points.")

def initialize_app():
    print("Initializing Database...")
    init_db()
    
    generate_initial_data()
    
    if not os.path.exists(config.MODEL_PATH):
        print("Training initial Random Forest model...")
        train_and_save_model()
    
if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
