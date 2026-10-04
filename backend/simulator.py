import threading
import time
import random

class TemperatureSimulator:
    def __init__(self):
        self.running = False
        self.scenario = "normal"
        self.current_temp = 28.0
        self.thread = None

    def start(self, scenario="normal"):
        self.scenario = scenario
        
        # Adjust base temperature if we are starting fresh
        # But if already running, just smoothly transition from current_temp
        if not self.running:
            if scenario == "normal":
                self.current_temp = 28.0
            elif scenario == "increasing":
                self.current_temp = 28.0
            elif scenario == "overheating":
                self.current_temp = 32.0
            else:
                self.current_temp = 28.0
            
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _run_loop(self):
        from backend.database import insert_reading
        from ml.prediction import predict_next_temperature, determine_status
        import backend
        
        while self.running:
            if self.scenario == "normal":
                self.current_temp += random.uniform(-0.5, 0.5)
                # Keep it bounded within normal operating bounds
                self.current_temp = max(20.0, min(35.0, self.current_temp))
            elif self.scenario == "increasing":
                # Gradual consistent increase
                self.current_temp += random.uniform(0.1, 0.6)
                # Cap at 50 so it doesn't go to infinity
                self.current_temp = min(50.0, self.current_temp)
            elif self.scenario == "overheating":
                # Sharp aggressive increase
                self.current_temp += random.uniform(0.5, 1.5)
                self.current_temp = min(60.0, self.current_temp)
            elif self.scenario == "random":
                # Random realistic variations
                self.current_temp += random.uniform(-1.5, 1.5)
                self.current_temp = max(15.0, min(45.0, self.current_temp))
            else:
                self.current_temp += random.uniform(-0.5, 0.5)
                
            temp_val = round(self.current_temp, 2)
            
            if backend.current_mode == "SIMULATION":
                try:
                    prediction = predict_next_temperature(temp_val)
                    status = determine_status(temp_val, prediction)
                    insert_reading(temp_val, "simulation", prediction, status)
                except Exception as e:
                    print(f"Simulator DB error: {e}")
                    
            time.sleep(2)
