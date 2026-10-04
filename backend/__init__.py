from backend.simulator import TemperatureSimulator
from backend.serial_reader import SerialReader

simulator = TemperatureSimulator()
serial_reader = SerialReader()

current_mode = "SIMULATION"

def set_mode(mode):
    global current_mode
    current_mode = mode
