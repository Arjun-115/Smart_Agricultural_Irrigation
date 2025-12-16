# predict.py placeholder
import json
from datetime import datetime
import joblib

# Load models
model_water = joblib.load("data/models/xgb_water.pkl")
model_fert = joblib.load("data/models/xgb_fertilizer.pkl")

# Simulated sensor reading (replace with real sensor input)
sensor_data = {
    "ldr_value": 54,
    "light_level": "Bright",
    "soil_ao_raw": 4095,
    "soil_moisture_percent": 0,
    "soil_do": "LOW",
    "soil_status": "Wet",
    "temperature_c": 3.4,
    "humidity_percent": 12.3,
    "heat_index_c": 0.12
}

# Prepare features
features = [[
    sensor_data["temperature_c"],
    sensor_data["humidity_percent"],
    sensor_data["soil_moisture_percent"],
    sensor_data["ldr_value"]
]]

# Predictions
irrigation_pred = model_water.predict(features)[0]
fertilizer_pred = model_fert.predict(features)[0]

predictions = {
    "irrigation": "ON" if irrigation_pred else "OFF",
    "fertilizer": "YES" if fertilizer_pred else "NO"
}

# Save to JSON
output = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "sensors": sensor_data,
    "predictions": predictions
}

filename = f"data/logs/prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, "w") as f:
    json.dump(output, f, indent=4)

print(f"Prediction saved: {filename}")
