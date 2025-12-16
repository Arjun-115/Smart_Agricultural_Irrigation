from pathlib import Path
import pandas as pd
import xgboost as xgb
import joblib
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.metrics import accuracy_score

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
processed_file = BASE_DIR / "data" / "processed" / "processed_data.csv"
models_folder = BASE_DIR / "data" / "models"
models_folder.mkdir(exist_ok=True)

# --- Load CSV ---
data = pd.read_csv(processed_file)
print("Processed data loaded successfully. Shape:", data.shape)

# --- Features and target ---
X = data[['TEMP_C','HUMIDITY','SOIL_PCT','LDR']]
y_water = data['irrigation_needed'].astype(int)

# --- Check class distribution ---
class_counts = y_water.value_counts()
print("Target class distribution:\n", class_counts)

# --- Safe train-test split ---
if class_counts.min() < 2:
    print("Dataset too small or too imbalanced. Training on all data.")
    X_train, y_train = X, y_water
    X_test, y_test = X, y_water
else:
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_idx, test_idx in sss.split(X, y_water):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_water.iloc[train_idx], y_water.iloc[test_idx]

# --- Check if training set has more than one class ---
if y_train.nunique() < 2:
    print("Training set contains only one class. Cannot train binary classifier.")
    print("Train on all data instead or collect more balanced data.")
    X_train, y_train = X, y_water
    X_test, y_test = X, y_water

print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
print("Training class distribution:", y_train.value_counts())

# --- Train XGBoost classifier ---
model_water = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    objective='binary:logistic',
    eval_metric='logloss',
    use_label_encoder=False
)

model_water.fit(X_train, y_train)

# --- Predictions ---
y_pred = model_water.predict(X_test)
if y_test.nunique() < 2:
    print("Test set has only one class. Accuracy cannot be computed reliably.")
else:
    acc = accuracy_score(y_test, y_pred)
    print(f"Water Prediction Accuracy: {acc:.4f}")

# --- Save model ---
model_path = models_folder / "xgb_water.pkl"
joblib.dump(model_water, model_path)
print(f"Model saved at {model_path}")
