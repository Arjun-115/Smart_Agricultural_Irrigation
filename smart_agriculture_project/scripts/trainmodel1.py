import serial
import time

PORT = "COM13"  # Change to your ESP32 COM port
BAUD = 115200

def send_command(cmd):
    try:
        with serial.Serial(PORT, BAUD, timeout=1) as ser:
            time.sleep(2)  # wait for ESP32 reset
            ser.write((cmd + "\n").encode())
            time.sleep(0.5)
            print(f"Sent command: {cmd}")

            # read response for 2 seconds
            end = time.time() + 2
            while time.time() < end:
                if ser.in_waiting > 0:
                    print(ser.readline().decode().strip())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    print("Turning motor ON continuously...")
    send_command("ON")
    print("Motor should now be ON.")
