import pandas as pd
import joblib
from pathlib import Path

# ============================================================
# CREDXAI - LOGISTIC REGRESSION EXPLAINABILITY
# ============================================================

MODEL_PATH = Path(
    "models/logistic_regression.pkl"
)

OUTPUT_PATH = Path(
    "outputs/logistic_feature_coefficients.csv"
)

print("=" * 70)
print("CREDXAI - MODEL EXPLAINABILITY")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load model
# ------------------------------------------------------------

print("\nLoading trained model...")

model = joblib.load(
    MODEL_PATH
)

print("Model loaded successfully.")

# ------------------------------------------------------------
# 2. Get preprocessing objects
# ------------------------------------------------------------

preprocessor = model.named_steps[
    "preprocessor"
]

classifier = model.named_steps[
    "classifier"
]

# ------------------------------------------------------------
# 3. Get transformed feature names
# ------------------------------------------------------------

feature_names = (
    preprocessor
    .get_feature_names_out()
)

coefficients = (
    classifier.coef_[0]
)

# ------------------------------------------------------------
# 4. Create coefficient table
# ------------------------------------------------------------

coef_df = pd.DataFrame(
    {
        "FEATURE": feature_names,
        "COEFFICIENT": coefficients
    }
)

coef_df["ABS_COEFFICIENT"] = (
    coef_df["COEFFICIENT"]
    .abs()
)

# ------------------------------------------------------------
# 5. Sort by coefficient
# ------------------------------------------------------------

positive = (
    coef_df
    .sort_values(
        "COEFFICIENT",
        ascending=False
    )
    .head(20)
)

negative = (
    coef_df
    .sort_values(
        "COEFFICIENT",
        ascending=True
    )
    .head(20)
)

# ------------------------------------------------------------
# 6. Print results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TOP FEATURES ASSOCIATED WITH HIGHER PREDICTED RISK")
print("=" * 70)

print(
    positive[
        [
            "FEATURE",
            "COEFFICIENT"
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 70)
print("TOP FEATURES ASSOCIATED WITH LOWER PREDICTED RISK")
print("=" * 70)

print(
    negative[
        [
            "FEATURE",
            "COEFFICIENT"
        ]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# 7. Overall strongest coefficients
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STRONGEST FEATURES BY ABSOLUTE COEFFICIENT")
print("=" * 70)

print(
    coef_df
    .sort_values(
        "ABS_COEFFICIENT",
        ascending=False
    )
    .head(30)[
        [
            "FEATURE",
            "COEFFICIENT"
        ]
    ]
    .to_string(index=False)
)

# ------------------------------------------------------------
# 8. Save
# ------------------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

coef_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved to:")
print(OUTPUT_PATH)

print("\nExplainability analysis completed.")
print("=" * 70)