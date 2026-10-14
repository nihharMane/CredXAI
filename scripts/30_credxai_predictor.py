import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - FINAL PREDICTION ENGINE
# ============================================================

MODEL_PATH = Path(
    "models/calibrated_logistic_regression.pkl"
)

DATA_PATH = Path(
    "data/processed/model_dataset.csv"
)

COEFFICIENT_PATH = Path(
    "outputs/logistic_feature_coefficients.csv"
)

print("=" * 70)
print("CREDXAI - FINAL PREDICTION ENGINE")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load model
# ------------------------------------------------------------

print("\nLoading calibrated model...")

model = joblib.load(
    MODEL_PATH
)

print("Model loaded successfully.")

# ------------------------------------------------------------
# 2. Load dataset
# ------------------------------------------------------------

print("\nLoading applicant data...")

df = pd.read_csv(
    DATA_PATH
)

print("Applicants:", len(df))

# ------------------------------------------------------------
# 3. Select applicant
# ------------------------------------------------------------

# For this first test we use the first applicant.
# Later we will allow an applicant ID to be entered.

applicant_index = 0

applicant = df.iloc[
    [applicant_index]
].copy()

actual_target = applicant[
    "TARGET"
].iloc[0]

applicant_id = applicant[
    "SK_ID_CURR"
].iloc[0]

# ------------------------------------------------------------
# 4. Prepare features
# ------------------------------------------------------------

X = applicant.drop(
    columns=["TARGET"],
    errors="ignore"
)

X = X.drop(
    columns=["SK_ID_CURR"],
    errors="ignore"
)

# ------------------------------------------------------------
# 5. Predict probability
# ------------------------------------------------------------

print("\nGenerating prediction...")

probability = model.predict_proba(
    X
)[0][1]

probability_percent = (
    probability * 100
)

# ------------------------------------------------------------
# 6. Risk band
# ------------------------------------------------------------

if probability < 0.10:

    risk_band = "LOW_RISK"

elif probability < 0.30:

    risk_band = "MEDIUM_RISK"

else:

    risk_band = "HIGH_RISK"

# ------------------------------------------------------------
# 7. Load feature coefficients
# ------------------------------------------------------------

coefficients = pd.read_csv(
    COEFFICIENT_PATH
)

# ------------------------------------------------------------
# 8. Extract feature names
# ------------------------------------------------------------

feature_column = None

for column in [
    "FEATURE",
    "feature",
    "Feature"
]:

    if column in coefficients.columns:

        feature_column = column
        break

if feature_column is None:

    raise ValueError(
        "Feature column not found in coefficient file."
    )

coefficient_column = None

for column in [
    "COEFFICIENT",
    "coefficient",
    "Coefficient"
]:

    if column in coefficients.columns:

        coefficient_column = column
        break

if coefficient_column is None:

    raise ValueError(
        "Coefficient column not found."
    )

# ------------------------------------------------------------
# 9. Identify strongest model factors
# ------------------------------------------------------------

coefficients[
    "ABS_COEFFICIENT"
] = coefficients[
    coefficient_column
].abs()

strongest = (
    coefficients
    .sort_values(
        "ABS_COEFFICIENT",
        ascending=False
    )
    .head(10)
)

# ------------------------------------------------------------
# 10. Generate risk explanation
# ------------------------------------------------------------

explanation = []

if probability >= 0.30:

    explanation.append(
        "The model estimates a relatively high "
        "probability of default."
    )

elif probability >= 0.10:

    explanation.append(
        "The model estimates a moderate "
        "probability of default."
    )

else:

    explanation.append(
        "The model estimates a relatively low "
        "probability of default."
    )

# ------------------------------------------------------------
# 11. Applicant financial information
# ------------------------------------------------------------

income = applicant[
    "AMT_INCOME_TOTAL"
].iloc[0]

credit = applicant[
    "AMT_CREDIT"
].iloc[0]

credit_to_income = applicant[
    "CREDIT_TO_INCOME"
].iloc[0]

age = applicant[
    "AGE_YEARS"
].iloc[0]

# Credit burden

if credit_to_income > 3:

    explanation.append(
        "The requested credit is high relative "
        "to reported income."
    )

elif credit_to_income < 1:

    explanation.append(
        "The requested credit is relatively low "
        "compared with reported income."
    )

# Age

if age < 25:

    explanation.append(
        "The applicant is relatively young."
    )

elif age >= 50:

    explanation.append(
        "The applicant is in an older age group."
    )

# Previous applications

previous_count = applicant[
    "PREVIOUS_APPLICATION_COUNT"
].iloc[0]

previous_refusals = applicant[
    "PREVIOUS_REFUSED_COUNT"
].iloc[0]

if previous_refusals > 0:

    explanation.append(
        f"The applicant has {int(previous_refusals)} "
        "previous refused application(s)."
    )

elif previous_count == 0:

    explanation.append(
        "No previous application history is available."
    )

# Payment behavior

late_ratio = applicant[
    "LATE_PAYMENT_RATIO"
].iloc[0]

if pd.notna(late_ratio):

    if late_ratio > 0.25:

        explanation.append(
            "The installment history shows a relatively "
            "high proportion of late payments."
        )

    elif late_ratio == 0:

        explanation.append(
            "No late installment-payment ratio was observed."
        )

# Bureau debt

debt_ratio = applicant[
    "DEBT_TO_CREDIT_RATIO"
].iloc[0]

if pd.notna(debt_ratio):

    if debt_ratio > 0.70:

        explanation.append(
            "Existing bureau debt represents a high "
            "share of total credit."
        )

# ------------------------------------------------------------
# 12. Final report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CREDXAI ASSESSMENT")
print("=" * 70)

print(
    f"\nApplicant ID: {applicant_id}"
)

print(
    f"Actual target (test only): {actual_target}"
)

print(
    f"\nDefault probability: "
    f"{probability_percent:.2f}%"
)

print(
    f"Risk band: {risk_band}"
)

print(
    f"\nIncome: {income:,.2f}"
)

print(
    f"Requested credit: {credit:,.2f}"
)

print(
    f"Credit-to-income ratio: "
    f"{credit_to_income:.3f}"
)

print(
    f"Age: {age:.2f} years"
)

print("\n" + "=" * 70)
print("MODEL EXPLANATION")
print("=" * 70)

print(
    "\nStrongest learned features:"
)

for _, row in strongest.iterrows():

    print(
        f"- {row[feature_column]}: "
        f"{row[coefficient_column]:.6f}"
    )

print(
    "\nApplicant-specific explanation:"
)

for reason in explanation:

    print(
        f"- {reason}"
    )

print("\n" + "=" * 70)
print("PREDICTION COMPLETED")
print("=" * 70)