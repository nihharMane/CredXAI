import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI
# Installment Payment Behaviour Feature Engineering
# ============================================================

INPUT_PATH = Path(
    "data/raw/home_credit/installments_payments.csv"
)

OUTPUT_PATH = Path(
    "data/processed/installment_features.csv"
)

print("=" * 70)
print("CREDXAI - INSTALLMENT PAYMENT FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load required columns
# ------------------------------------------------------------

columns = [
    "SK_ID_CURR",
    "SK_ID_PREV",
    "NUM_INSTALMENT_VERSION",
    "NUM_INSTALMENT_NUMBER",
    "DAYS_INSTALMENT",
    "DAYS_ENTRY_PAYMENT",
    "AMT_INSTALMENT",
    "AMT_PAYMENT"
]

print("\nLoading installment data...")

df = pd.read_csv(
    INPUT_PATH,
    usecols=columns
)

print("Rows loaded:", len(df))
print("Columns loaded:", len(df.columns))

# ------------------------------------------------------------
# 2. Calculate payment delay
# ------------------------------------------------------------

# DAYS_INSTALMENT = expected payment day
# DAYS_ENTRY_PAYMENT = actual payment day
#
# Positive value means payment happened after expected date.
#
df["PAYMENT_DELAY"] = (
    df["DAYS_ENTRY_PAYMENT"]
    - df["DAYS_INSTALMENT"]
)

# ------------------------------------------------------------
# 3. Late payment flag
# ------------------------------------------------------------

df["LATE_PAYMENT"] = (
    df["PAYMENT_DELAY"] > 0
).astype(int)

# ------------------------------------------------------------
# 4. Severe late payment flag
# ------------------------------------------------------------

df["SEVERE_LATE_PAYMENT"] = (
    df["PAYMENT_DELAY"] > 30
).astype(int)

# ------------------------------------------------------------
# 5. Payment amount ratio
# ------------------------------------------------------------

df["PAYMENT_RATIO"] = (
    df["AMT_PAYMENT"]
    /
    df["AMT_INSTALMENT"].replace(0, np.nan)
)

# ------------------------------------------------------------
# 6. Aggregate by applicant
# ------------------------------------------------------------

features = (
    df.groupby("SK_ID_CURR")
    .agg(
        INSTALLMENT_COUNT=(
            "SK_ID_PREV",
            "count"
        ),

        UNIQUE_PREVIOUS_LOANS=(
            "SK_ID_PREV",
            "nunique"
        ),

        AVG_PAYMENT_DELAY=(
            "PAYMENT_DELAY",
            "mean"
        ),

        MAX_PAYMENT_DELAY=(
            "PAYMENT_DELAY",
            "max"
        ),

        AVG_PAYMENT_RATIO=(
            "PAYMENT_RATIO",
            "mean"
        ),

        TOTAL_INSTALLMENT_AMOUNT=(
            "AMT_INSTALMENT",
            "sum"
        ),

        TOTAL_PAYMENT_AMOUNT=(
            "AMT_PAYMENT",
            "sum"
        ),

        AVG_INSTALLMENT_AMOUNT=(
            "AMT_INSTALMENT",
            "mean"
        ),

        AVG_PAYMENT_AMOUNT=(
            "AMT_PAYMENT",
            "mean"
        ),

        LATE_PAYMENT_COUNT=(
            "LATE_PAYMENT",
            "sum"
        ),

        SEVERE_LATE_PAYMENT_COUNT=(
            "SEVERE_LATE_PAYMENT",
            "sum"
        )
    )
    .reset_index()
)

# ------------------------------------------------------------
# 7. Late payment ratio
# ------------------------------------------------------------

features["LATE_PAYMENT_RATIO"] = (
    features["LATE_PAYMENT_COUNT"]
    /
    features["INSTALLMENT_COUNT"]
)

# ------------------------------------------------------------
# 8. Severe late payment ratio
# ------------------------------------------------------------

features["SEVERE_LATE_PAYMENT_RATIO"] = (
    features["SEVERE_LATE_PAYMENT_COUNT"]
    /
    features["INSTALLMENT_COUNT"]
)

# ------------------------------------------------------------
# 9. Overall payment ratio
# ------------------------------------------------------------

features["OVERALL_PAYMENT_RATIO"] = (
    features["TOTAL_PAYMENT_AMOUNT"]
    /
    features["TOTAL_INSTALLMENT_AMOUNT"]
    .replace(0, np.nan)
)

# ------------------------------------------------------------
# 10. Save
# ------------------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

features.to_csv(
    OUTPUT_PATH,
    index=False
)

# ------------------------------------------------------------
# 11. Report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("INSTALLMENT FEATURES CREATED")
print("=" * 70)

print(
    "Applicants with installment history:",
    len(features)
)

print("\nFeature columns:")

for column in features.columns:
    print("-", column)

print("\nFirst 5 rows:")
print(
    features.head().to_string()
)

print("\nMissing values:")
print(
    features.isnull()
    .sum()
    .sort_values(ascending=False)
    .head(20)
)

print("\nSaved to:")
print(OUTPUT_PATH)

print("\nFeature engineering completed.")