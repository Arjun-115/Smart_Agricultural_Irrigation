# smart_agriculture_project/scripts/preprocess_data.py
import pandas as pd
import numpy as np
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
raw_file = BASE_DIR / "data" / "raw" / "data.csv"          # your raw sensor/raw dataset
processed_file = BASE_DIR / "data" / "processed" / "processed_data.csv"
processed_file.parent.mkdir(exist_ok=True, parents=True)

# --- Load raw data ---
if not raw_file.exists():
    raise FileNotFoundError(f"Raw data not found at {raw_file}")

data = pd.read_csv(raw_file)
print("Raw data loaded. Shape:", data.shape)

# --- Inspect and clean ---
print("Checking for missing values...")
print(data.isna().sum())

# Fill missing numeric values with mean
numeric_cols = ['TEMP_C','HUMIDITY','SOIL_PCT','LDR']  # adjust according to your CSV
for col in numeric_cols:
    if col in data.columns:
        data[col] = data[col].fillna(data[col].mean())

# Convert categorical columns (e.g., soil status, light level) to numeric
categorical_cols = ['SOIL_STATUS','LIGHT_LEVEL']
for col in categorical_cols:
    if col in data.columns:
        data[col] = data[col].fillna('Unknown')
        data = pd.get_dummies(data, columns=[col])

# Optional: add derived features
if 'TEMP_C' in data.columns and 'HUMIDITY' in data.columns:
    data['heat_index'] = 0.5 * (data['TEMP_C'] + 61.0 + ((data['TEMP_C']-68.0)*1.2) + (data['HUMIDITY']*0.094))

# Optional: normalize numeric features (0-1 scale)
for col in numeric_cols:
    if col in data.columns:
        min_val = data[col].min()
        max_val = data[col].max()
        if max_val > min_val:
            data[col] = (data[col] - min_val) / (max_val - min_val)

# --- Add seasonal one-hot encoding (example if you have a 'season' column) ---
if 'season' in data.columns:
    data = pd.get_dummies(data, columns=['season'])

# --- Add target columns if not present ---
# Example: irrigation_needed, fertilizer_needed
if 'irrigation_needed' not in data.columns:
    data['irrigation_needed'] = (data['SOIL_PCT'] < 40).astype(int)  # simple threshold
if 'fertilizer_needed' not in data.columns:
    data['fertilizer_needed'] = (data['TEMP_C'] < 0.5).astype(int)  # placeholder logic

# --- Save processed data ---
data.to_csv(processed_file, index=False)
print("Processed data saved at:", processed_file)
print("Processed data shape:", data.shape)
