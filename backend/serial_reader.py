import serial
import threading
import time
from config import ARDUINO_PORT, BAUD_RATE

class SerialReader:
    def __init__(self):
        self.running = False
        self.thread = None
        self.serial_conn = None
        self.status = "NOT CONNECTED"

    def start(self):
        if self.running:
            return
            
        try:
            self.serial_conn = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
            self.status = "CONNECTED"
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            self.status = f"ERROR: {str(e)}"
            print(f"Serial connection error: {e}")

    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.status = "NOT CONNECTED"

    def _run_loop(self):
        from backend.database import insert_reading
        from ml.prediction import predict_next_temperature, determine_status
        import backend
        
        while self.running:
            if self.serial_conn and self.serial_conn.is_open:
                try:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line.startswith("TEMP:") and backend.current_mode == "HARDWARE":
                        try:
                            temp_val = round(float(line.split(":")[1]), 2)
                            prediction = predict_next_temperature(temp_val)
                            status = determine_status(temp_val, prediction)
                            insert_reading(temp_val, "hardware", prediction, status)
                        except ValueError:
                            pass
                except Exception as e:
                    print(f"Serial read error: {e}")
            time.sleep(1)
