from flask import Blueprint, jsonify, request, render_template
from backend.database import get_latest_readings, insert_reading, get_db_connection
from ml.prediction import predict_next_temperature, determine_status, load_model
from ml.train_model import train_and_save_model
from backend import simulator, serial_reader
import backend

api = Blueprint('api', __name__)

@api.route('/')
@api.route('/history.html')
@api.route('/system.html')
def index():
    return render_template('index.html')

@api.route('/api/analytics', methods=['GET'])
def analytics():
    from backend.database import get_analytics
    return jsonify(get_analytics())

@api.route('/api/alerts', methods=['GET'])
def alerts():
    from backend.database import get_alerts
    return jsonify(get_alerts())

@api.route('/api/sensor-data', methods=['POST'])
def receive_data():
    data = request.json
    temperature = data.get('temperature')
    source = data.get('source')
    
    if temperature is None or source is None:
        return jsonify({"error": "Invalid data"}), 400
        
    if source == 'simulation' and backend.current_mode != 'SIMULATION':
        return jsonify({"message": "Ignored, in hardware mode"}), 200
    if source == 'hardware' and backend.current_mode != 'HARDWARE':
        return jsonify({"message": "Ignored, in simulation mode"}), 200

    prediction = predict_next_temperature(temperature)
    status = determine_status(temperature, prediction)
    
    inserted = insert_reading(temperature, source, prediction, status)
    return jsonify(inserted), 201

@api.route('/api/latest', methods=['GET'])
def latest():
    readings = get_latest_readings(limit=50)
    return jsonify(readings)

@api.route('/api/history', methods=['GET'])
def history_endpoint():
    readings = get_latest_readings(limit=200)
    return jsonify(readings)

@api.route('/api/status', methods=['GET'])
def status_endpoint():
    db_status = "CONNECTED"
    ml_status = "READY" if load_model() else "NOT TRAINED"
    
    return jsonify({
        "backend": "ONLINE",
        "database": db_status,
        "ml_model": ml_status,
        "mode": backend.current_mode,
        "arduino": serial_reader.status,
        "simulator_running": simulator.running,
        "simulator_scenario": simulator.scenario
    })

@api.route('/api/simulation/start', methods=['POST'])
def start_sim():
    scenario = request.json.get('scenario', 'normal')
    simulator.start(scenario)
    return jsonify({"message": "Simulation started"})

@api.route('/api/simulation/stop', methods=['POST'])
def stop_sim():
    simulator.stop()
    return jsonify({"message": "Simulation stopped"})

@api.route('/api/simulation/scenario', methods=['POST'])
def set_scenario():
    scenario = request.json.get('scenario', 'normal')
    simulator.scenario = scenario
    return jsonify({"message": f"Scenario set to {scenario}"})

@api.route('/api/mode', methods=['POST'])
def set_mode():
    new_mode = request.json.get('mode')
    if new_mode in ['SIMULATION', 'HARDWARE']:
        backend.current_mode = new_mode
        if new_mode == 'HARDWARE':
            simulator.stop()
            serial_reader.start()
        else:
            serial_reader.stop()
        return jsonify({"message": f"Mode set to {new_mode}"})
    return jsonify({"error": "Invalid mode"}), 400

@api.route('/api/ml/retrain', methods=['POST'])
def retrain():
    success, msg = train_and_save_model()
    return jsonify({"success": success, "message": msg})
