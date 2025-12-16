# smart_agriculture_project/scripts/collect_sensors_json.py
import serial
import time
import json
import os
import sys
import serial.tools.list_ports
from datetime import datetime

# --------------------- CONFIG ---------------------
BAUD = 115200
JSON_FILE = "../data/raw/data.json"  # relative path from scripts folder
AUTO_DETECT_COM = True  # set False to use fixed PORT
READ_INTERVAL = 2       # seconds between readings
# --------------------------------------------------

# Function to auto-detect ESP32 COM port
def detect_esp32_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description or "UART" in port.description:
            return port.device
    return None

# Detect or set PORT
if AUTO_DETECT_COM:
    PORT = detect_esp32_port()
    if PORT is None:
        print("ESP32 not found. Please connect it and try again.")
        sys.exit(1)
else:
    PORT = "COM13"  # change manually if not auto-detecting

# Ensure JSON folder exists
os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)

# Connect to ESP32
try:
    esp = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)  # wait for ESP32 to boot
    print(f"Connected to ESP32 on {PORT}")
except Exception as e:
    print("Failed to open serial port:", e)
    sys.exit(1)

# Initialize JSON file if not exists
if not os.path.isfile(JSON_FILE):
    with open(JSON_FILE, 'w') as f:
        json.dump([], f, indent=4)

print("Collecting data from ESP32 in real-time... Press Ctrl+C to stop.")

try:
    while True:
        try:
            line = esp.readline().decode(errors="ignore").strip()
        except Exception as e:
            print("Serial read error:", e)
            continue

        if line.startswith("ts="):
            parts = line.split(";")
            data_dict = {p.split("=")[0].strip(): p.split("=")[1].strip()
                         for p in parts if "=" in p}

            # Add system timestamp
            data_dict["system_timestamp"] = datetime.now().isoformat()

            # Load existing JSON, append new entry, write back
            try:
                with open(JSON_FILE, 'r+') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []

                    existing_data.append(data_dict)

                    f.seek(0)
                    json.dump(existing_data, f, indent=4)
                    f.truncate()  # remove leftover content
                    f.flush()
                    os.fsync(f.fileno())

                print("Saved:", data_dict)
            except Exception as e:
                print("Error writing to JSON:", e)

        time.sleep(READ_INTERVAL)

except KeyboardInterrupt:
    print("\nData collection stopped by user.")
    esp.close()
