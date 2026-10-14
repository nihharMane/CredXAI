import joblib
import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - SAVED MODEL PREDICTION TEST
# ============================================================

MODEL_PATH = Path(
    "models/calibrated_logistic_regression.pkl"
)

DATA_PATH = Path(
    "data/processed/model_dataset.csv"
)

print("=" * 70)
print("CREDXAI - SAVED MODEL PREDICTION TEST")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load model
# ------------------------------------------------------------

print("\nLoading calibrated model...")

model = joblib.load(
    MODEL_PATH
)

print("Model loaded successfully.")
print("Model type:", type(model))

# ------------------------------------------------------------
# 2. Load model dataset
# ------------------------------------------------------------

print("\nLoading model dataset...")

df = pd.read_csv(
    DATA_PATH
)

print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 3. Separate target
# ------------------------------------------------------------

X = df.drop(
    columns=["TARGET"]
)

y = df["TARGET"]

# ------------------------------------------------------------
# 4. Remove ID if present
# ------------------------------------------------------------

if "SK_ID_CURR" in X.columns:

    X = X.drop(
        columns=["SK_ID_CURR"]
    )

# ------------------------------------------------------------
# 5. Select one applicant
# ------------------------------------------------------------

sample = X.iloc[[0]]

actual_target = y.iloc[0]

print("\n" + "=" * 70)
print("TEST APPLICANT")
print("=" * 70)

print(
    sample.to_string(index=False)
)

print(
    "\nActual target:",
    actual_target
)

# ------------------------------------------------------------
# 6. Prediction
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL PREDICTION")
print("=" * 70)

probability = model.predict_proba(
    sample
)[0][1]

prediction = model.predict(
    sample
)[0]

print(
    f"Predicted default probability: "
    f"{probability:.6f}"
)

print(
    f"Predicted class: {prediction}"
)

print(
    f"Predicted probability percentage: "
    f"{probability * 100:.2f}%"
)

# ------------------------------------------------------------
# 7. Risk band
# ------------------------------------------------------------

if probability < 0.10:

    risk = "LOW_RISK"

elif probability < 0.30:

    risk = "MEDIUM_RISK"

else:

    risk = "HIGH_RISK"

print(
    "\nRisk band:",
    risk
)

# ------------------------------------------------------------
# 8. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL PREDICTION TEST COMPLETED")
print("=" * 70)
