import serial
import time
import pandas as pd
import joblib  # for loading XGBoost model

# ---------------- CONFIG ----------------
ESP_PORT = "COM13"      # Your ESP32 serial port
BAUD = 115200
MODEL_PATH = "../data/models/xgb_water.pkl"
READ_INTERVAL = 5       # seconds between readings
# ---------------------------------------

# Load trained model
model = joblib.load(MODEL_PATH)
print("Model loaded successfully.")

# Serial connection to ESP32
ser = serial.Serial(ESP_PORT, BAUD, timeout=1)
time.sleep(2)  # wait for ESP32 reset

def send_motor_command(cmd):
    """Send ON/OFF command to ESP32 motor"""
    ser.write((cmd + "\n").encode())
    print(f"Motor command sent: {cmd}")

def parse_sensor_line(line):
    """
    Parse sensor line from ESP32 into a dictionary
    Format expected from ESP32:
    ts=00:01:23; TEMP_C=25.0; HUMIDITY=60.0; SOIL_PCT=45; SOIL_STATUS=Wet; LDR=2000; LIGHT_LEVEL=Bright
    """
    data = {}
    try:
        parts = line.strip().split(";")
        for p in parts:
            key, val = p.split("=")
            key = key.strip()
            val = val.strip()
            if key in ["TEMP_C", "HUMIDITY", "SOIL_PCT", "LDR"]:
                data[key] = float(val)
            else:
                data[key] = val
        return data
    except:
        return None

def preprocess_for_model(sensor_data):
    """
    Convert ESP32 sensor data into DataFrame with same features as model
    """
    df = pd.DataFrame([sensor_data])
    
    # Example: keep only features used during training
    features = ["TEMP_C", "HUMIDITY", "SOIL_PCT", "LDR"]  # adapt if your model uses more
    return df[features]

def main_loop():
    motor_status = "OFF"
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            sensor_data = parse_sensor_line(line)
            if sensor_data:
                print("Sensor data:", sensor_data)
                
                # Prepare features
                X = preprocess_for_model(sensor_data)
                
                # Predict irrigation_needed
                y_pred = model.predict(X)[0]
                print("Predicted irrigation_needed:", y_pred)
                
                # Control motor
                if y_pred == 1 and motor_status == "OFF":
                    send_motor_command("ON")
                    motor_status = "ON"
                elif y_pred == 0 and motor_status == "ON":
                    send_motor_command("OFF")
                    motor_status = "OFF"
                
        time.sleep(READ_INTERVAL)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Stopping...")
        send_motor_command("OFF")
        ser.close()
