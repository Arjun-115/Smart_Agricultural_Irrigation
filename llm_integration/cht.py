import json
from transformers import pipeline

chatbot = pipeline("text-generation", model="sarvamai/sarvam-m", device=-1)

# Read Arduino/ESP32 JSON data
with open("data/raw/data.json") as f:
    sensor = json.load(f)

prompt = f"""
Temperature: {sensor['temperature']}°C
Humidity: {sensor['humidity']}%
Soil Moisture: {sensor['moisture']}%
Give advice in local language for farmers.
"""

response = chatbot(prompt, max_length=150)[0]["generated_text"]
print(response)
