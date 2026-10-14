import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI
# BUREAU CREDIT HISTORY FEATURE ENGINEERING
# ============================================================

INPUT_PATH = Path(
    "data/raw/home_credit/bureau.csv"
)

OUTPUT_PATH = Path(
    "data/processed/bureau_features.csv"
)

print("=" * 70)
print("CREDXAI - BUREAU CREDIT FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load required columns
# ------------------------------------------------------------

columns = [
    "SK_ID_CURR",
    "SK_ID_BUREAU",
    "CREDIT_ACTIVE",
    "CREDIT_CURRENCY",
    "DAYS_CREDIT",
    "CREDIT_DAY_OVERDUE",
    "DAYS_CREDIT_ENDDATE",
    "DAYS_ENDDATE_FACT",
    "AMT_CREDIT_MAX_OVERDUE",
    "CNT_CREDIT_PROLONG",
    "AMT_CREDIT_SUM",
    "AMT_CREDIT_SUM_DEBT",
    "AMT_CREDIT_SUM_LIMIT",
    "AMT_CREDIT_SUM_OVERDUE",
    "AMT_ANNUITY",
    "CREDIT_TYPE"
]

print("\nLoading bureau data...")

df = pd.read_csv(
    INPUT_PATH,
    usecols=columns
)

print("Rows loaded:", len(df))
print("Columns loaded:", len(df.columns))

# ------------------------------------------------------------
# 2. Active / closed credit flags
# ------------------------------------------------------------

df["ACTIVE_CREDIT_FLAG"] = (
    df["CREDIT_ACTIVE"]
    .eq("Active")
    .astype(int)
)

df["CLOSED_CREDIT_FLAG"] = (
    df["CREDIT_ACTIVE"]
    .eq("Closed")
    .astype(int)
)

# ------------------------------------------------------------
# 3. Overdue flags
# ------------------------------------------------------------

df["OVERDUE_FLAG"] = (
    df["CREDIT_DAY_OVERDUE"] > 0
).astype(int)

df["OVERDUE_AMOUNT_FLAG"] = (
    df["AMT_CREDIT_SUM_OVERDUE"] > 0
).astype(int)

# ------------------------------------------------------------
# 4. Aggregate by applicant
# ------------------------------------------------------------

features = (
    df.groupby("SK_ID_CURR")
    .agg(

        BUREAU_CREDIT_COUNT=(
            "SK_ID_BUREAU",
            "count"
        ),

        UNIQUE_BUREAU_CREDITS=(
            "SK_ID_BUREAU",
            "nunique"
        ),

        ACTIVE_CREDIT_COUNT=(
            "ACTIVE_CREDIT_FLAG",
            "sum"
        ),

        CLOSED_CREDIT_COUNT=(
            "CLOSED_CREDIT_FLAG",
            "sum"
        ),

        AVG_DAYS_CREDIT=(
            "DAYS_CREDIT",
            "mean"
        ),

        MIN_DAYS_CREDIT=(
            "DAYS_CREDIT",
            "min"
        ),

        AVG_CREDIT_DAY_OVERDUE=(
            "CREDIT_DAY_OVERDUE",
            "mean"
        ),

        MAX_CREDIT_DAY_OVERDUE=(
            "CREDIT_DAY_OVERDUE",
            "max"
        ),

        OVERDUE_CREDIT_COUNT=(
            "OVERDUE_FLAG",
            "sum"
        ),

        OVERDUE_AMOUNT_COUNT=(
            "OVERDUE_AMOUNT_FLAG",
            "sum"
        ),

        TOTAL_OVERDUE_AMOUNT=(
            "AMT_CREDIT_SUM_OVERDUE",
            "sum"
        ),

        MAX_OVERDUE_AMOUNT=(
            "AMT_CREDIT_SUM_OVERDUE",
            "max"
        ),

        AVG_CREDIT_AMOUNT=(
            "AMT_CREDIT_SUM",
            "mean"
        ),

        TOTAL_CREDIT_AMOUNT=(
            "AMT_CREDIT_SUM",
            "sum"
        ),

        TOTAL_CREDIT_DEBT=(
            "AMT_CREDIT_SUM_DEBT",
            "sum"
        ),

        AVG_CREDIT_DEBT=(
            "AMT_CREDIT_SUM_DEBT",
            "mean"
        ),

        TOTAL_CREDIT_LIMIT=(
            "AMT_CREDIT_SUM_LIMIT",
            "sum"
        ),

        AVG_CREDIT_LIMIT=(
            "AMT_CREDIT_SUM_LIMIT",
            "mean"
        ),

        AVG_CREDIT_ANNUITY=(
            "AMT_ANNUITY",
            "mean"
        ),

        TOTAL_CREDIT_PROLONG=(
            "CNT_CREDIT_PROLONG",
            "sum"
        )
    )
    .reset_index()
)

# ------------------------------------------------------------
# 5. Ratios
# ------------------------------------------------------------

features["ACTIVE_CREDIT_RATIO"] = (
    features["ACTIVE_CREDIT_COUNT"]
    /
    features["BUREAU_CREDIT_COUNT"]
)

features["OVERDUE_CREDIT_RATIO"] = (
    features["OVERDUE_CREDIT_COUNT"]
    /
    features["BUREAU_CREDIT_COUNT"]
)

features["OVERDUE_AMOUNT_RATIO"] = (
    features["OVERDUE_AMOUNT_COUNT"]
    /
    features["BUREAU_CREDIT_COUNT"]
)

features["DEBT_TO_CREDIT_RATIO"] = (
    features["TOTAL_CREDIT_DEBT"]
    /
    features["TOTAL_CREDIT_AMOUNT"]
    .replace(0, np.nan)
)

features["CREDIT_LIMIT_UTILIZATION"] = (
    features["TOTAL_CREDIT_DEBT"]
    /
    features["TOTAL_CREDIT_LIMIT"]
    .replace(0, np.nan)
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
print("BUREAU FEATURES CREATED")
print("=" * 70)

print(
    "Applicants with bureau history:",
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

print("\nCredit active status distribution:")

print(
    df["CREDIT_ACTIVE"]
    .value_counts(dropna=False)
)

print("\nSaved to:")

print(OUTPUT_PATH)

print("\nFeature engineering completed.")