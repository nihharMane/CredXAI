import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - FINAL DECISION REPORT
# ============================================================

MODEL_PATH = Path(
    "models/calibrated_logistic_regression.pkl"
)

DATA_PATH = Path(
    "data/processed/model_dataset.csv"
)

OUTPUT_PATH = Path(
    "outputs/final_decision_report.csv"
)

print("=" * 70)
print("CREDXAI - FINAL DECISION REPORT")
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
# 4. PREPARE MODEL INPUT
# ------------------------------------------------------------

X = applicant.drop(
    columns=["TARGET", "SK_ID_CURR"],
    errors="ignore"
)

# ------------------------------------------------------------
# 5. PREDICT
# ------------------------------------------------------------

probability = model.predict_proba(X)[0][1]

probability_percent = probability * 100

# ------------------------------------------------------------
# 6. RISK BAND
# ------------------------------------------------------------

if probability < 0.10:

    risk_band = "LOW_RISK"

elif probability < 0.30:

    risk_band = "MEDIUM_RISK"

else:

    risk_band = "HIGH_RISK"

# ------------------------------------------------------------
# 7. GET ORIGINAL LOGISTIC PIPELINE
# ------------------------------------------------------------

calibrated_classifier = model.calibrated_classifiers_[0]

pipeline = calibrated_classifier.estimator

preprocessor = pipeline.named_steps["preprocessor"]

classifier = pipeline.named_steps["classifier"]

# ------------------------------------------------------------
# 8. TRANSFORM APPLICANT
# ------------------------------------------------------------

X_transformed = preprocessor.transform(X)

if hasattr(X_transformed, "toarray"):

    X_transformed = X_transformed.toarray()

# ------------------------------------------------------------
# 9. FEATURE CONTRIBUTIONS
# ------------------------------------------------------------

feature_names = preprocessor.get_feature_names_out()

coefficients = classifier.coef_[0]

contributions = (
    X_transformed[0] * coefficients
)

contribution_df = pd.DataFrame({

    "FEATURE": feature_names,

    "VALUE": X_transformed[0],

    "COEFFICIENT": coefficients,

    "CONTRIBUTION": contributions

})

# ------------------------------------------------------------
# 10. POSITIVE / NEGATIVE FACTORS
# ------------------------------------------------------------

positive = (
    contribution_df[
        contribution_df["CONTRIBUTION"] > 0
    ]
    .sort_values(
        "CONTRIBUTION",
        ascending=False
    )
    .head(5)
)

negative = (
    contribution_df[
        contribution_df["CONTRIBUTION"] < 0
    ]
    .sort_values(
        "CONTRIBUTION",
        ascending=True
    )
    .head(5)
)

# ------------------------------------------------------------
# 11. APPLICANT FINANCIAL INFORMATION
# ------------------------------------------------------------

income = applicant[
    "AMT_INCOME_TOTAL"
].iloc[0]

credit = applicant[
    "AMT_CREDIT"
].iloc[0]

annuity = applicant[
    "AMT_ANNUITY"
].iloc[0]

age = applicant[
    "AGE_YEARS"
].iloc[0]

credit_to_income = applicant[
    "CREDIT_TO_INCOME"
].iloc[0]

previous_count = applicant[
    "PREVIOUS_APPLICATION_COUNT"
].iloc[0]

previous_refusals = applicant[
    "PREVIOUS_REFUSED_COUNT"
].iloc[0]

late_payment_ratio = applicant[
    "LATE_PAYMENT_RATIO"
].iloc[0]

# ------------------------------------------------------------
# 12. INTERPRETATION
# ------------------------------------------------------------

if probability < 0.10:

    interpretation = (
        "The applicant has a relatively low estimated "
        "probability of default."
    )

elif probability < 0.30:

    interpretation = (
        "The applicant has a moderate estimated "
        "probability of default."
    )

else:

    interpretation = (
        "The applicant has a relatively high estimated "
        "probability of default."
    )

# ------------------------------------------------------------
# 13. ADDITIONAL OBSERVATIONS
# ------------------------------------------------------------

observations = []

if credit_to_income > 3:

    observations.append(
        "High requested credit relative to income."
    )

elif credit_to_income < 1:

    observations.append(
        "Requested credit is relatively low compared "
        "with income."
    )

if previous_refusals > 0:

    observations.append(
        f"{int(previous_refusals)} previous application(s) "
        "were refused."
    )

if previous_count > 0:

    observations.append(
        f"{int(previous_count)} previous application(s) "
        "are available."
    )

if pd.notna(late_payment_ratio):

    if late_payment_ratio > 0.25:

        observations.append(
            "Relatively high late-payment ratio."
        )

    elif late_payment_ratio == 0:

        observations.append(
            "No late-payment ratio was observed."
        )

# ------------------------------------------------------------
# 14. DISPLAY FINAL REPORT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CREDXAI ASSESSMENT")
print("=" * 70)

print(
    f"\nApplicant ID: {applicant_id}"
)

print(
    f"Default Probability: "
    f"{probability_percent:.2f}%"
)

print(
    f"Risk Band: {risk_band}"
)

print(
    f"\nIncome: ₹{income:,.2f}"
)

print(
    f"Requested Credit: ₹{credit:,.2f}"
)

print(
    f"Annual Annuity: ₹{annuity:,.2f}"
)

print(
    f"Age: {age:.2f} years"
)

print(
    f"Credit-to-Income Ratio: "
    f"{credit_to_income:.3f}"
)

print("\n" + "=" * 70)
print("RISK-INCREASING FACTORS")
print("=" * 70)

for _, row in positive.iterrows():

    print(
        f"↑ {row['FEATURE']}"
        f" | Contribution: "
        f"{row['CONTRIBUTION']:.4f}"
    )

print("\n" + "=" * 70)
print("RISK-REDUCING FACTORS")
print("=" * 70)

for _, row in negative.iterrows():

    print(
        f"↓ {row['FEATURE']}"
        f" | Contribution: "
        f"{row['CONTRIBUTION']:.4f}"
    )

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

print(
    f"\n{interpretation}"
)

if observations:

    print("\nApplicant observations:")

    for observation in observations:

        print(
            f"- {observation}"
        )

print("\n" + "=" * 70)
print("IMPORTANT")
print("=" * 70)

print(
    "\nThis assessment is a machine-learning-based "
    "risk estimate and should support, not replace, "
    "human credit decisions."
)

# ------------------------------------------------------------
# 15. SAVE REPORT
# ------------------------------------------------------------

report = {

    "APPLICANT_ID":
        applicant_id,

    "DEFAULT_PROBABILITY":
        probability,

    "DEFAULT_PROBABILITY_PERCENT":
        probability_percent,

    "RISK_BAND":
        risk_band,

    "INCOME":
        income,

    "REQUESTED_CREDIT":
        credit,

    "ANNUITY":
        annuity,

    "AGE":
        age,

    "CREDIT_TO_INCOME":
        credit_to_income,

    "PREVIOUS_APPLICATION_COUNT":
        previous_count,

    "PREVIOUS_REFUSED_COUNT":
        previous_refusals,

    "LATE_PAYMENT_RATIO":
        late_payment_ratio,

    "ACTUAL_TARGET_TEST_ONLY":
        actual_target,

    "INTERPRETATION":
        interpretation

}

report_df = pd.DataFrame([report])

report_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nReport saved to:")

print(
    OUTPUT_PATH
)

print("\n" + "=" * 70)
print("FINAL DECISION REPORT COMPLETED")
print("=" * 70)
