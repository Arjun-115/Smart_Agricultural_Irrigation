import serial
import time

PORT = "COM13"   # change if needed
BAUD = 115200

try:
    esp = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)   # wait for ESP32 to boot
except Exception as e:
    print("Failed to open serial:", e)
    raise SystemExit

def send(cmd, wait=0.2):
    esp.write((cmd + "\n").encode())
    time.sleep(wait)
    reply = esp.read_all().decode(errors="ignore")
    print("ESP32 →", reply.strip())

print("Connected. Sending commands...")

send("run")        # Motor ON
time.sleep(3)      # run duration
send("state")
time.sleep(0.2)

send("stop")       # Motor OFF
time.sleep(0.2)
send("state")

esp.close()
print("Done.")
