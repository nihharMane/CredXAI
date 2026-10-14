import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI
# POS / CASH LOAN BEHAVIOUR FEATURE ENGINEERING
# ============================================================

INPUT_PATH = Path(
    "data/raw/home_credit/POS_CASH_balance.csv"
)

OUTPUT_PATH = Path(
    "data/processed/pos_cash_features.csv"
)

print("=" * 70)
print("CREDXAI - POS / CASH FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load required columns
# ------------------------------------------------------------

columns = [
    "SK_ID_PREV",
    "SK_ID_CURR",
    "MONTHS_BALANCE",
    "CNT_INSTALMENT",
    "CNT_INSTALMENT_FUTURE",
    "NAME_CONTRACT_STATUS",
    "SK_DPD",
    "SK_DPD_DEF"
]

print("\nLoading POS/CASH data...")

df = pd.read_csv(
    INPUT_PATH,
    usecols=columns
)

print("Rows loaded:", len(df))
print("Columns loaded:", len(df.columns))

# ------------------------------------------------------------
# 2. Delinquency flags
# ------------------------------------------------------------

df["DPD_FLAG"] = (
    df["SK_DPD"] > 0
).astype(int)

df["DPD_DEFAULT_FLAG"] = (
    df["SK_DPD_DEF"] > 0
).astype(int)

# ------------------------------------------------------------
# 3. Contract status flags
# ------------------------------------------------------------

df["COMPLETED_FLAG"] = (
    df["NAME_CONTRACT_STATUS"]
    .eq("Completed")
    .astype(int)
)

df["ACTIVE_FLAG"] = (
    df["NAME_CONTRACT_STATUS"]
    .eq("Active")
    .astype(int)
)

# ------------------------------------------------------------
# 4. Aggregate by applicant
# ------------------------------------------------------------

features = (
    df.groupby("SK_ID_CURR")
    .agg(

        POS_CASH_RECORD_COUNT=(
            "SK_ID_PREV",
            "count"
        ),

        POS_CASH_LOAN_COUNT=(
            "SK_ID_PREV",
            "nunique"
        ),

        AVG_INSTALLMENT_COUNT=(
            "CNT_INSTALMENT",
            "mean"
        ),

        AVG_INSTALLMENTS_FUTURE=(
            "CNT_INSTALMENT_FUTURE",
            "mean"
        ),

        AVG_POS_DPD=(
            "SK_DPD",
            "mean"
        ),

        MAX_POS_DPD=(
            "SK_DPD",
            "max"
        ),

        POS_DPD_COUNT=(
            "DPD_FLAG",
            "sum"
        ),

        POS_DPD_DEFAULT_COUNT=(
            "DPD_DEFAULT_FLAG",
            "sum"
        ),

        POS_COMPLETED_COUNT=(
            "COMPLETED_FLAG",
            "sum"
        ),

        POS_ACTIVE_COUNT=(
            "ACTIVE_FLAG",
            "sum"
        )
    )
    .reset_index()
)

# ------------------------------------------------------------
# 5. Ratios
# ------------------------------------------------------------

features["POS_DPD_RATIO"] = (
    features["POS_DPD_COUNT"]
    /
    features["POS_CASH_RECORD_COUNT"]
)

features["POS_DPD_DEFAULT_RATIO"] = (
    features["POS_DPD_DEFAULT_COUNT"]
    /
    features["POS_CASH_RECORD_COUNT"]
)

features["POS_COMPLETED_RATIO"] = (
    features["POS_COMPLETED_COUNT"]
    /
    features["POS_CASH_RECORD_COUNT"]
)

features["POS_ACTIVE_RATIO"] = (
    features["POS_ACTIVE_COUNT"]
    /
    features["POS_CASH_RECORD_COUNT"]
)

# ------------------------------------------------------------
# 6. Save
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
# 7. Report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("POS / CASH FEATURES CREATED")
print("=" * 70)

print(
    "Applicants with POS/CASH history:",
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

print("\nContract status distribution:")
print(
    df["NAME_CONTRACT_STATUS"]
    .value_counts(dropna=False)
)

print("\nSaved to:")
print(OUTPUT_PATH)

print("\nFeature engineering completed.")