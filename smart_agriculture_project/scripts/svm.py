from pathlib import Path
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
processed_file = BASE_DIR / "data" / "processed" / "processed_data.csv"
models_folder = BASE_DIR / "data" / "models"
models_folder.mkdir(exist_ok=True)

# --- Load CSV ---
if not processed_file.exists():
    raise FileNotFoundError(f"Processed CSV not found at: {processed_file}")

data = pd.read_csv(processed_file)
print("Processed data loaded successfully")

# --- Features and targets ---
X = data[['temperature_c','humidity_percent','soil_moisture_percent','ldr_value']]
y_water = data['irrigation_needed'].astype(int)

# --- Stratified split ---
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in sss.split(X, y_water):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y_water.iloc[train_idx], y_water.iloc[test_idx]

# --- Scale features (important for SVM) ---
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- Train SVM classifier ---
svm_model = SVC(
    kernel='rbf',        # radial basis function kernel
    C=1.0,               # regularization parameter
    gamma='scale',       # kernel coefficient
    probability=True,    # enable probability predictions
    random_state=42
)

svm_model.fit(X_train_scaled, y_train)
y_pred = svm_model.predict(X_test_scaled)
print("SVM Water Prediction Accuracy:", accuracy_score(y_test, y_pred))

# --- Save SVM model and scaler ---
joblib.dump(svm_model, models_folder / "svm_water.pkl")
joblib.dump(scaler, models_folder / "svm_scaler.pkl")
print(f"SVM model and scaler saved at {models_folder}")
