import pandas as pd
import json
from pathlib import Path
import time
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
raw_json_file = BASE_DIR / "data" / "raw" / "data.json"
processed_folder = BASE_DIR / "data" / "processed"
processed_folder.mkdir(exist_ok=True, parents=True)
processed_file = processed_folder / "processed_data.csv"
scaler_file = processed_folder / "scaler_stats.json"

# expected columns / header (keeps raw values)
cols = [
    "time", "TEMP_C", "HUMIDITY", "SOIL_PCT", "SOIL_STATUS", "LDR",
    "LIGHT_LEVEL", "system_timestamp", "soil_status", "light_level",
    "heat_index", "irrigation_needed", "fertilizer_needed"
]

if not processed_file.exists():
    pd.DataFrame(columns=cols).to_csv(processed_file, index=False)

# load persistent scaler stats if present
if scaler_file.exists():
    try:
        scaler_stats = json.loads(scaler_file.read_text())
    except Exception:
        scaler_stats = {}
else:
    scaler_stats = {}

print("Starting continuous preprocessing... Press Ctrl+C to stop.")

try:
    while True:
        # Load JSON data
        try:
            with open(raw_json_file, 'r') as f:
                json_data = json.load(f)
        except Exception as e:
            print("Error reading JSON:", e)
            time.sleep(2)
            continue

        if not json_data:
            time.sleep(2)
            continue

        new_data = pd.DataFrame(json_data)

        # quick debug of raw input (very helpful)
        numeric_cols = ['TEMP_C', 'HUMIDITY', 'SOIL_PCT', 'LDR']
        print("--- New raw batch sample ---")
        print(new_data[numeric_cols].head().to_string())

        # parse timestamp if present
        if 'system_timestamp' in new_data.columns:
            new_data['system_timestamp'] = pd.to_datetime(new_data['system_timestamp'], errors='coerce')

        # ensure numeric (but don't overwrite raw permanently)
        for col in numeric_cols:
            if col in new_data.columns:
                new_data[col] = pd.to_numeric(new_data[col], errors='coerce')

        # read existing data once
        existing_cols = pd.read_csv(processed_file, nrows=0).columns.tolist()
        existing_data = pd.read_csv(processed_file, parse_dates=['system_timestamp'] if 'system_timestamp' in existing_cols else None)

        # fill missing using historic mean when available, else batch mean, else 0
        for col in numeric_cols:
            if col in new_data.columns:
                historic_mean = None
                if col in existing_data.columns and not existing_data[col].dropna().empty:
                    historic_mean = existing_data[col].dropna().mean()
                batch_mean = new_data[col].mean()
                fill_val = historic_mean if historic_mean is not None else (batch_mean if not np.isnan(batch_mean) else 0.0)
                new_data[col] = new_data[col].fillna(fill_val)

        # encode categorical columns
        if 'SOIL_STATUS' in new_data.columns:
            new_data['soil_status'] = new_data['SOIL_STATUS'].map({'Wet': 0, 'Dry': 1}).fillna(0).astype(int)
        else:
            new_data['soil_status'] = 0

        if 'LIGHT_LEVEL' in new_data.columns:
            new_data['light_level'] = new_data['LIGHT_LEVEL'].map({'Dark': 0, 'Dim': 1, 'Bright': 2}).fillna(1).astype(int)
        else:
            new_data['light_level'] = 1

        # compute targets on RAW values - keep them raw
        if 'SOIL_PCT' in new_data.columns:
            # convert percent->fraction only if values >1
            if new_data['SOIL_PCT'].max() > 1.0:
                new_data['SOIL_PCT_raw'] = new_data['SOIL_PCT'] / 100.0
            else:
                new_data['SOIL_PCT_raw'] = new_data['SOIL_PCT']
            new_data['irrigation_needed'] = (new_data['SOIL_PCT_raw'] < 0.4).astype(int)
        else:
            new_data['irrigation_needed'] = 0

        if 'TEMP_C' in new_data.columns:
            new_data['fertilizer_needed'] = (new_data['TEMP_C'] < 15.0).astype(int)
        else:
            new_data['fertilizer_needed'] = 0

        # heat index (convert C->F -> formula -> back to C). Keep raw heat_index column
        if 'TEMP_C' in new_data.columns and 'HUMIDITY' in new_data.columns:
            T_f = new_data['TEMP_C'] * 9.0/5.0 + 32.0
            RH = new_data['HUMIDITY']
            HI_f = 0.5 * (T_f + 61.0 + ((T_f - 68.0)*1.2) + (RH * 0.094))
            new_data['heat_index'] = (HI_f - 32.0) * 5.0/9.0
        else:
            new_data['heat_index'] = np.nan

        # --- Normalization step but produce *_norm columns instead of overwriting raw ---
        to_scale = numeric_cols + ['heat_index']
        for col in to_scale:
            if col not in new_data.columns:
                continue

            # get persistent min/max if available
            hist_min = scaler_stats.get(col, {}).get('min', None)
            hist_max = scaler_stats.get(col, {}).get('max', None)

            batch_min = float(new_data[col].min())
            batch_max = float(new_data[col].max())

            # combine
            if hist_min is None or hist_max is None:
                global_min = batch_min
                global_max = batch_max
            else:
                global_min = min(hist_min, batch_min)
                global_max = max(hist_max, batch_max)

            # when range is too small, skip normalization and set norm to 0.0 or batch-centered value
            eps = 1e-6
            if global_max - global_min > eps:
                new_data[f"{col}_norm"] = (new_data[col] - global_min) / (global_max - global_min)
            else:
                # no meaningful range: put 0.0 or 0.5 as neutral value
                new_data[f"{col}_norm"] = 0.0

            # persist back the stats
            scaler_stats[col] = {'min': global_min, 'max': global_max}

        # Save scaler_stats to disk
        try:
            scaler_file.write_text(json.dumps(scaler_stats))
        except Exception as e:
            print("Warning: could not save scaler stats:", e)

        # Deduplicate using iso timestamp string if available, else drop exact duplicates
        if 'system_timestamp' in new_data.columns and 'system_timestamp' in existing_data.columns:
            existing_ts = existing_data['system_timestamp'].astype(str).tolist()
            new_data = new_data[~new_data['system_timestamp'].astype(str).isin(existing_ts)]
        else:
            new_data = new_data.drop_duplicates()

        # If no rows left, continue
        if new_data.empty:
            print("No new rows after dedupe.")
            time.sleep(2)
            continue

        # Keep only the columns expected in CSV (and add *_norm cols if present)
        out_cols = cols[:]  # base
        for c in list(new_data.columns):
            if c.endswith("_norm") and c not in out_cols:
                out_cols.append(c)
            if c not in out_cols and c in cols:
                out_cols.append(c)

        # append
        combined_data = pd.concat([existing_data, new_data.reindex(columns=existing_data.columns.union(new_data.columns))], ignore_index=True)
        combined_data.to_csv(processed_file, index=False)
        print(f"{len(new_data)} new rows appended. Total rows: {combined_data.shape[0]}")
        print("Sample stored (raw->norm):")
        for col in numeric_cols:
            if col in new_data.columns and f"{col}_norm" in new_data.columns:
                print(f" {col}: raw min={new_data[col].min():.3f}, max={new_data[col].max():.3f} -> norm min={new_data[f'{col}_norm'].min():.3f}, max={new_data[f'{col}_norm'].max():.3f}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopped by user.")
