import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI
# Credit Card Behaviour Feature Engineering
# ============================================================

INPUT_PATH = Path(
    "data/raw/home_credit/credit_card_balance.csv"
)

OUTPUT_PATH = Path(
    "data/processed/credit_card_features.csv"
)

print("=" * 70)
print("CREDXAI - CREDIT CARD FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load required columns
# ------------------------------------------------------------

columns = [
    "SK_ID_CURR",
    "SK_ID_PREV",
    "MONTHS_BALANCE",
    "AMT_BALANCE",
    "AMT_CREDIT_LIMIT_ACTUAL",
    "AMT_DRAWINGS_ATM_CURRENT",
    "AMT_DRAWINGS_CURRENT",
    "AMT_DRAWINGS_OTHER_CURRENT",
    "AMT_DRAWINGS_POS_CURRENT",
    "AMT_INST_MIN_REGULARITY",
    "AMT_PAYMENT_CURRENT",
    "AMT_PAYMENT_TOTAL_CURRENT",
    "CNT_DRAWINGS_ATM_CURRENT",
    "CNT_DRAWINGS_CURRENT",
    "CNT_DRAWINGS_OTHER_CURRENT",
    "CNT_DRAWINGS_POS_CURRENT",
    "CNT_INSTALMENT_MATURE_CUM",
    "SK_DPD",
    "SK_DPD_DEF"
]

print("\nLoading credit-card data...")

df = pd.read_csv(
    INPUT_PATH,
    usecols=columns
)

print("Rows loaded:", len(df))
print("Columns loaded:", len(df.columns))

# ------------------------------------------------------------
# 2. Credit utilization
# ------------------------------------------------------------

df["CREDIT_UTILIZATION"] = (
    df["AMT_BALANCE"]
    /
    df["AMT_CREDIT_LIMIT_ACTUAL"].replace(0, np.nan)
)

# ------------------------------------------------------------
# 3. Payment ratio
# ------------------------------------------------------------

df["CARD_PAYMENT_RATIO"] = (
    df["AMT_PAYMENT_TOTAL_CURRENT"]
    /
    df["AMT_BALANCE"].replace(0, np.nan)
)

# ------------------------------------------------------------
# 4. Default/delinquency indicators
# ------------------------------------------------------------

df["DPD_FLAG"] = (
    df["SK_DPD"] > 0
).astype(int)

df["DPD_DEF_FLAG"] = (
    df["SK_DPD_DEF"] > 0
).astype(int)

# ------------------------------------------------------------
# 5. Aggregate by applicant
# ------------------------------------------------------------

features = (
    df.groupby("SK_ID_CURR")
    .agg(

        CREDIT_CARD_RECORD_COUNT=(
            "SK_ID_PREV",
            "count"
        ),

        CREDIT_CARD_COUNT=(
            "SK_ID_PREV",
            "nunique"
        ),

        AVG_CARD_BALANCE=(
            "AMT_BALANCE",
            "mean"
        ),

        MAX_CARD_BALANCE=(
            "AMT_BALANCE",
            "max"
        ),

        AVG_CREDIT_LIMIT=(
            "AMT_CREDIT_LIMIT_ACTUAL",
            "mean"
        ),

        MAX_CREDIT_LIMIT=(
            "AMT_CREDIT_LIMIT_ACTUAL",
            "max"
        ),

        AVG_CREDIT_UTILIZATION=(
            "CREDIT_UTILIZATION",
            "mean"
        ),

        MAX_CREDIT_UTILIZATION=(
            "CREDIT_UTILIZATION",
            "max"
        ),

        AVG_CARD_PAYMENT=(
            "AMT_PAYMENT_TOTAL_CURRENT",
            "mean"
        ),

        TOTAL_CARD_PAYMENT=(
            "AMT_PAYMENT_TOTAL_CURRENT",
            "sum"
        ),

        AVG_CARD_PAYMENT_RATIO=(
            "CARD_PAYMENT_RATIO",
            "mean"
        ),

        TOTAL_DRAWINGS=(
            "AMT_DRAWINGS_CURRENT",
            "sum"
        ),

        AVG_DRAWINGS=(
            "AMT_DRAWINGS_CURRENT",
            "mean"
        ),

        TOTAL_ATM_DRAWINGS=(
            "AMT_DRAWINGS_ATM_CURRENT",
            "sum"
        ),

        TOTAL_POS_DRAWINGS=(
            "AMT_DRAWINGS_POS_CURRENT",
            "sum"
        ),

        TOTAL_OTHER_DRAWINGS=(
            "AMT_DRAWINGS_OTHER_CURRENT",
            "sum"
        ),

        AVG_DRAWING_COUNT=(
            "CNT_DRAWINGS_CURRENT",
            "mean"
        ),

        TOTAL_DRAWING_COUNT=(
            "CNT_DRAWINGS_CURRENT",
            "sum"
        ),

        AVG_DPD=(
            "SK_DPD",
            "mean"
        ),

        MAX_DPD=(
            "SK_DPD",
            "max"
        ),

        DPD_COUNT=(
            "DPD_FLAG",
            "sum"
        ),

        DPD_DEFAULT_COUNT=(
            "DPD_DEF_FLAG",
            "sum"
        )
    )
    .reset_index()
)

# ------------------------------------------------------------
# 6. DPD ratios
# ------------------------------------------------------------

features["DPD_RATIO"] = (
    features["DPD_COUNT"]
    /
    features["CREDIT_CARD_RECORD_COUNT"]
)

features["DPD_DEFAULT_RATIO"] = (
    features["DPD_DEFAULT_COUNT"]
    /
    features["CREDIT_CARD_RECORD_COUNT"]
)

# ------------------------------------------------------------
# 7. Save
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
# 8. Report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CREDIT CARD FEATURES CREATED")
print("=" * 70)

print(
    "Applicants with credit-card history:",
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