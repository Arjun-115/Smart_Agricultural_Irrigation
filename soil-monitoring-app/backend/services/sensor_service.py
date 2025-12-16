import json
from pathlib import Path

_current_mode = "auto"
_manual_state = "off"

# Path to your raw sensor JSON file
DATA_FILE = Path("D:/Project36/smart_agriculture_project/data/raw/data.json")

# Load sensor records
try:
    with open(DATA_FILE, "r") as f:
        _sensor_records = json.load(f)
except Exception as e:
    print(f"Error loading JSON file: {e}")
    _sensor_records = []

_index = 0  # pointer to current record

def _get_next_record():
    """Return the next record from JSON in a loop."""
    global _index
    if not _sensor_records:
        return {}
    record = _sensor_records[_index]
    _index = (_index + 1) % len(_sensor_records)
    return record

# Sensor functions
def get_dummy_moisture():
    record = _get_next_record()
    return float(record.get("SOIL_PCT", 0))

def get_dummy_humidity():
    record = _get_next_record()
    return float(record.get("HUMIDITY", 0))

def get_dummy_ldr():
    record = _get_next_record()
    return float(record.get("LDR", 0))

def get_dummy_temperature():
    record = _get_next_record()
    return float(record.get("TEMP_C", 0)) * 10


def get_dummy_water_status():
    record = _get_next_record()
    soil = float(record.get("SOIL_PCT", 0))
    return soil < 30  # True if watering needed

# Switch functions
def get_mode():
    return _current_mode

def set_mode(mode: str):
    global _current_mode
    if mode not in ["manual", "auto"]:
        return {"error": "Invalid mode"}
    _current_mode = mode
    return {"message": "Mode updated", "mode": _current_mode}

def manual_switch(state: str):
    global _manual_state
    if state not in ["on", "off"]:
        return {"error": "Invalid state"}
    _manual_state = state
    return {"message": f"Pump turned {state}", "state": _manual_state}
