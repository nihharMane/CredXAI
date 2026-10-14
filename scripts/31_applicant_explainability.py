import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - APPLICANT SPECIFIC EXPLAINABILITY
# ============================================================

MODEL_PATH = Path(
    "models/calibrated_logistic_regression.pkl"
)

DATA_PATH = Path(
    "data/processed/model_dataset.csv"
)

print("=" * 70)
print("CREDXAI - APPLICANT SPECIFIC EXPLAINABILITY")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD MODEL
# ------------------------------------------------------------

print("\nLoading calibrated model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")

# ------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------

print("\nLoading applicant data...")

df = pd.read_csv(DATA_PATH)

print("Applicants:", len(df))

# ------------------------------------------------------------
# 3. SELECT APPLICANT
# ------------------------------------------------------------

applicant_index = 0

applicant = df.iloc[[applicant_index]].copy()

applicant_id = applicant["SK_ID_CURR"].iloc[0]

actual_target = applicant["TARGET"].iloc[0]

# ------------------------------------------------------------
# 4. PREPARE FEATURES
# ------------------------------------------------------------

X = applicant.drop(
    columns=["TARGET", "SK_ID_CURR"],
    errors="ignore"
)

# ------------------------------------------------------------
# 5. PREDICTION
# ------------------------------------------------------------

probability = model.predict_proba(X)[0][1]

# ------------------------------------------------------------
# 6. GET LOGISTIC MODEL
# ------------------------------------------------------------

# CalibratedClassifierCV contains fitted classifiers.
# Each classifier contains the original Pipeline.

calibrated_classifier = model.calibrated_classifiers_[0]

pipeline = calibrated_classifier.estimator

preprocessor = pipeline.named_steps["preprocessor"]

classifier = pipeline.named_steps["classifier"]

# ------------------------------------------------------------
# 7. TRANSFORM APPLICANT
# ------------------------------------------------------------

X_transformed = preprocessor.transform(X)

if hasattr(X_transformed, "toarray"):
    X_transformed = X_transformed.toarray()

# ------------------------------------------------------------
# 8. FEATURE NAMES
# ------------------------------------------------------------

feature_names = preprocessor.get_feature_names_out()

coefficients = classifier.coef_[0]

# ------------------------------------------------------------
# 9. APPLICANT FEATURE CONTRIBUTIONS
# ------------------------------------------------------------

contributions = (
    X_transformed[0] * coefficients
)

explanation_df = pd.DataFrame({
    "FEATURE": feature_names,
    "VALUE": X_transformed[0],
    "COEFFICIENT": coefficients,
    "CONTRIBUTION": contributions
})

# ------------------------------------------------------------
# 10. SORT CONTRIBUTIONS
# ------------------------------------------------------------

positive = (
    explanation_df[
        explanation_df["CONTRIBUTION"] > 0
    ]
    .sort_values(
        "CONTRIBUTION",
        ascending=False
    )
    .head(10)
)

negative = (
    explanation_df[
        explanation_df["CONTRIBUTION"] < 0
    ]
    .sort_values(
        "CONTRIBUTION",
        ascending=True
    )
    .head(10)
)

# ------------------------------------------------------------
# 11. RISK BAND
# ------------------------------------------------------------

if probability < 0.10:

    risk_band = "LOW_RISK"

elif probability < 0.30:

    risk_band = "MEDIUM_RISK"

else:

    risk_band = "HIGH_RISK"

# ------------------------------------------------------------
# 12. DISPLAY RESULT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CREDXAI APPLICANT ASSESSMENT")
print("=" * 70)

print(
    f"\nApplicant ID: {applicant_id}"
)

print(
    f"Actual target (testing only): {actual_target}"
)

print(
    f"Default probability: {probability * 100:.2f}%"
)

print(
    f"Risk band: {risk_band}"
)

# ------------------------------------------------------------
# 13. RISK-INCREASING FACTORS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FACTORS INCREASING PREDICTED RISK")
print("=" * 70)

if len(positive) == 0:

    print("No significant positive contributions found.")

else:

    for _, row in positive.iterrows():

        print(
            f"↑ {row['FEATURE']}: "
            f"contribution = {row['CONTRIBUTION']:.4f}"
        )

# ------------------------------------------------------------
# 14. RISK-REDUCING FACTORS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FACTORS REDUCING PREDICTED RISK")
print("=" * 70)

if len(negative) == 0:

    print("No significant negative contributions found.")

else:

    for _, row in negative.iterrows():

        print(
            f"↓ {row['FEATURE']}: "
            f"contribution = {row['CONTRIBUTION']:.4f}"
        )

# ------------------------------------------------------------
# 15. SAVE FULL CONTRIBUTIONS
# ------------------------------------------------------------

output_path = Path(
    "outputs/applicant_feature_contributions.csv"
)

explanation_df[
    [
        "FEATURE",
        "VALUE",
        "COEFFICIENT",
        "CONTRIBUTION"
    ]
].sort_values(
    "CONTRIBUTION",
    ascending=False
).to_csv(
    output_path,
    index=False
)

print("\n" + "=" * 70)
print("EXPLAINABILITY OUTPUT")
print("=" * 70)

print(
    f"\nSaved to:\n{output_path}"
)

print("\nApplicant-specific explainability completed.")

print("=" * 70)