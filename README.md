# AI-Based Machine Temperature Prediction & Monitoring System

## 1. Project Overview
Our system monitors machine temperature and uses a Random Forest Regressor to predict the next temperature. In the absence of hardware, a Python simulator generates realistic temperature readings. Both simulated and real Arduino readings pass through the same Flask backend, SQLite database, and ML pipeline. When hardware becomes available, Arduino with an LM35 sensor sends temperature readings through USB serial to Python, so the existing dashboard and ML system can be reused.

## 2. Features
- **Real-Time Monitoring**: Display current temperature with dynamic trend indicators.
- **AI Prediction**: Uses Random Forest Regressor to predict the next temperature reading.
- **Dual Data Sources**: Seamlessly switch between Simulation Mode and Hardware Mode.
- **Data Persistence**: All readings are stored in a local SQLite database.
- **Visual Analytics**: Interactive web-based dashboard using Chart.js with a clean light theme.
- **Threshold Warnings**: Automatic determination of Normal, Warning, and High-Risk statuses based on predicted temperatures.

## 3. Technologies Used
- **Backend**: Python, Flask, SQLite
- **Machine Learning**: Scikit-learn (RandomForestRegressor), Pandas, NumPy, Joblib
- **Frontend**: HTML5, Vanilla CSS (White/Light Theme), JavaScript, Chart.js
- **Hardware Integration**: PySerial, Arduino, LM35 Sensor

## 4. Folder Structure
```
Temperature-Prediction/
├── app.py
├── requirements.txt
├── README.md
├── config.py
├── backend/
│   ├── __init__.py
│   ├── database.py
│   ├── routes.py
│   ├── simulator.py
│   └── serial_reader.py
├── ml/
│   ├── train_model.py
│   ├── prediction.py
│   └── feature_engineering.py
├── data/
│   └── temperature.db (auto-generated)
├── arduino/
│   └── temperature_sensor.ino
└── frontend/
    ├── index.html
    ├── history.html
    ├── system.html
    ├── css/
    │   └── style.css
    └── js/
        ├── dashboard.js
        ├── history.js
        └── system.js
```

## 5. Installation
1. Ensure Python 3.8+ is installed on your computer.
2. Open a terminal or command prompt in the project directory.
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 6. How to Run
1. With your virtual environment activated, start the Flask server:
   ```bash
   python app.py
   ```
2. The application will automatically create the database and train the initial ML model if they do not exist.
3. Open your browser and go to `http://127.0.0.1:5000`.

## 7. Simulation Mode
1. Ensure the Mode selector on the left sidebar is set to **Simulation**.
2. Click **Start** button on the top right.
3. You can change the scenario (Normal, Increasing, Overheating, Random) to see how the system and AI model react.
4. Click **Stop** when you want to pause data generation.

## 8. Hardware Mode
When you have the hardware:
1. Connect your Arduino to your laptop.
2. Ensure you have uploaded the Arduino code (see section 10).
3. Find your Arduino's COM port.
4. In `config.py`, change `ARDUINO_PORT` to your actual COM port (e.g., `COM3` on Windows, `/dev/ttyUSB0` on Mac/Linux).
5. Run `python app.py`.
6. Select **Hardware** in the Mode selector on the dashboard. The system will start reading from the Arduino.

## 9. Arduino Wiring
- **LM35 Temperature Sensor**:
  - VCC to Arduino 5V
  - OUT to Arduino A0
  - GND to Arduino GND
- **Green LED**: Anode (long leg) to Arduino D7 (with 220-ohm resistor), Cathode to GND
- **Red LED**: Anode (long leg) to Arduino D8 (with 220-ohm resistor), Cathode to GND
- **Buzzer**: Positive to Arduino D9, Negative to GND

## 10. Arduino IDE Instructions
1. Open the Arduino IDE.
2. Open the file `arduino/temperature_sensor.ino` from this project.
3. Go to Tools -> Board and select **Arduino Uno**.
4. Go to Tools -> Port and select your connected COM port.
5. Click the **Upload** button (right arrow icon).
6. Close the Arduino IDE Serial Monitor before running the Python app (only one program can use the COM port at a time).

## 11. How Python Reads Arduino
The Python backend uses the `pyserial` library. The `SerialReader` class connects to the configured COM port at a 9600 baud rate. It listens for lines starting with `TEMP:`, extracts the numeric value, and sends it to the same Flask pipeline used by the simulator.

## 12. How Random Forest Works
The system uses a Random Forest Regressor from scikit-learn.
It predicts the *next* temperature based on historical features:
- `temperature`: Current reading
- `previous_temperature`: Reading before current
- `recent_average`: Average of the last 3 readings
- `temperature_change`: Difference between current and previous

The model is trained automatically on startup if `model.pkl` is missing. You can retrain it anytime via the dashboard using the latest database readings.

## 13. Database Structure
We use SQLite (`temperature.db`). The main table is `temperature_data`:
- `id`: Primary key
- `timestamp`: Date and time of reading
- `temperature`: Actual temperature recorded
- `source`: 'simulation' or 'hardware'
- `prediction`: The AI's predicted next temperature
- `status`: 'NORMAL', 'WARNING', or 'HIGH RISK'

## 14. API Endpoints
- `GET /`: Dashboard
- `GET /api/latest`: Returns the most recent 50 temperature readings
- `GET /api/status`: Returns system status (DB, ML, Mode, Arduino)
- `POST /api/sensor-data`: Accepts JSON `{"temperature": 25.0, "source": "simulation"}`
- `POST /api/simulation/start`: Starts the simulator
- `POST /api/simulation/stop`: Stops the simulator
- `POST /api/simulation/scenario`: Changes simulation logic
- `POST /api/mode`: Switches between SIMULATION and HARDWARE
- `POST /api/ml/retrain`: Triggers a retraining of the ML model

## 15. How to Switch Simulation → Hardware
Simply change the dropdown on the left sidebar from **Simulation** to **Hardware**. The backend will automatically stop the Python simulator and start the `SerialReader` thread.

## 16. Troubleshooting
- **Port already in use**: Close the Arduino IDE Serial Monitor. Only one application can read the COM port.
- **Model errors**: Ensure you have let the simulator run a bit to generate data, then click "Retrain Model".
- **ModuleNotFoundError**: Ensure your virtual environment is activated and `pip install -r requirements.txt` ran successfully.

## 17. Viva Explanation
"Our system monitors machine temperature and uses a Random Forest Regressor to predict the next temperature. In the absence of hardware, a Python simulator generates realistic temperature readings. Both simulated and real Arduino readings pass through the same Flask backend, SQLite database and ML pipeline. When hardware becomes available, Arduino with an LM35 sensor sends temperature readings through USB serial to Python, so the existing dashboard and ML system can be reused."
