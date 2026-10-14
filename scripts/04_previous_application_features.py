import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI
# Previous Application Feature Engineering
# ============================================================

INPUT_PATH = Path(
    "data/raw/home_credit/previous_application.csv"
)

OUTPUT_PATH = Path(
    "data/processed/previous_application_features.csv"
)

print("=" * 70)
print("CREDXAI - PREVIOUS APPLICATION FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load required columns only
# ------------------------------------------------------------

columns = [
    "SK_ID_CURR",
    "SK_ID_PREV",
    "AMT_APPLICATION",
    "AMT_CREDIT",
    "AMT_DOWN_PAYMENT",
    "AMT_GOODS_PRICE",
    "AMT_ANNUITY",
    "NAME_CONTRACT_STATUS",
    "NAME_CONTRACT_TYPE",
    "DAYS_DECISION",
    "CNT_PAYMENT"
]

print("\nLoading previous applications...")

df = pd.read_csv(
    INPUT_PATH,
    usecols=columns
)

print("Rows loaded:", len(df))
print("Columns loaded:", len(df.columns))

# ------------------------------------------------------------
# 2. Basic application counts
# ------------------------------------------------------------

features = (
    df.groupby("SK_ID_CURR")
    .agg(
        PREVIOUS_APPLICATION_COUNT=(
            "SK_ID_PREV",
            "count"
        )
    )
    .reset_index()
)

# ------------------------------------------------------------
# 3. Approved applications
# ------------------------------------------------------------

approved = (
    df.assign(
        APPROVED_FLAG=(
            df["NAME_CONTRACT_STATUS"]
            .eq("Approved")
            .astype(int)
        )
    )
    .groupby("SK_ID_CURR")["APPROVED_FLAG"]
    .sum()
    .reset_index(
        name="PREVIOUS_APPROVED_COUNT"
    )
)

features = features.merge(
    approved,
    on="SK_ID_CURR",
    how="left"
)

# ------------------------------------------------------------
# 4. Refused applications
# ------------------------------------------------------------

refused = (
    df.assign(
        REFUSED_FLAG=(
            df["NAME_CONTRACT_STATUS"]
            .eq("Refused")
            .astype(int)
        )
    )
    .groupby("SK_ID_CURR")["REFUSED_FLAG"]
    .sum()
    .reset_index(
        name="PREVIOUS_REFUSED_COUNT"
    )
)

features = features.merge(
    refused,
    on="SK_ID_CURR",
    how="left"
)

# ------------------------------------------------------------
# 5. Cancelled applications
# ------------------------------------------------------------

cancelled = (
    df.assign(
        CANCELLED_FLAG=(
            df["NAME_CONTRACT_STATUS"]
            .eq("Canceled")
            .astype(int)
        )
    )
    .groupby("SK_ID_CURR")["CANCELLED_FLAG"]
    .sum()
    .reset_index(
        name="PREVIOUS_CANCELLED_COUNT"
    )
)

features = features.merge(
    cancelled,
    on="SK_ID_CURR",
    how="left"
)

# ------------------------------------------------------------
# 6. Application amounts
# ------------------------------------------------------------

amount_features = (
    df.groupby("SK_ID_CURR")
    .agg(
        PREVIOUS_AVG_APPLICATION_AMOUNT=(
            "AMT_APPLICATION",
            "mean"
        ),

        PREVIOUS_AVG_CREDIT_AMOUNT=(
            "AMT_CREDIT",
            "mean"
        ),

        PREVIOUS_MAX_CREDIT_AMOUNT=(
            "AMT_CREDIT",
            "max"
        ),

        PREVIOUS_AVG_DOWN_PAYMENT=(
            "AMT_DOWN_PAYMENT",
            "mean"
        ),

        PREVIOUS_AVG_GOODS_PRICE=(
            "AMT_GOODS_PRICE",
            "mean"
        ),

        PREVIOUS_AVG_ANNUITY=(
            "AMT_ANNUITY",
            "mean"
        )
    )
    .reset_index()
)

features = features.merge(
    amount_features,
    on="SK_ID_CURR",
    how="left"
)

# ------------------------------------------------------------
# 7. Approval rate
# ------------------------------------------------------------

features["PREVIOUS_APPROVAL_RATE"] = (
    features["PREVIOUS_APPROVED_COUNT"]
    /
    features["PREVIOUS_APPLICATION_COUNT"]
)

# ------------------------------------------------------------
# 8. Refusal rate
# ------------------------------------------------------------

features["PREVIOUS_REFUSAL_RATE"] = (
    features["PREVIOUS_REFUSED_COUNT"]
    /
    features["PREVIOUS_APPLICATION_COUNT"]
)

# ------------------------------------------------------------
# 9. Credit-to-application ratio
# ------------------------------------------------------------

features["PREVIOUS_CREDIT_TO_APPLICATION"] = (
    features["PREVIOUS_AVG_CREDIT_AMOUNT"]
    /
    features["PREVIOUS_AVG_APPLICATION_AMOUNT"]
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
print("PREVIOUS APPLICATION FEATURES CREATED")
print("=" * 70)

print("Applicants with previous applications:", len(features))

print("\nFeature columns:")

for column in features.columns:
    print("-", column)

print("\nFirst 5 rows:")
print(features.head().to_string())

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