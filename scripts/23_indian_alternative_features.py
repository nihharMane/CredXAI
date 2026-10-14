import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - INDIAN ALTERNATIVE DATA FEATURES
# ============================================================

INPUT = Path(
    "data/external/Customer_financial_profiles.csv"
)

OUTPUT = Path(
    "data/processed/indian_alternative_features.csv"
)

print("=" * 70)
print("CREDXAI - INDIAN ALTERNATIVE DATA FEATURES")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

print("\nLoading Indian financial data...")

df = pd.read_csv(INPUT)

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

print("Rows:", len(df))
print("Unique clients:", df["client_id"].nunique())

# ------------------------------------------------------------
# 2. Client-level static information
# ------------------------------------------------------------

client = (
    df.groupby("client_id")
    .agg(
        AGE=("current_age", "first"),
        YEARLY_INCOME=("yearly_income", "first"),
        PER_CAPITA_INCOME=("per_capita_income", "first"),
        TOTAL_DEBT=("total_debt", "first"),
        CREDIT_SCORE=("credit_score", "first"),
        NUM_CREDIT_CARDS=("num_credit_cards", "first"),
    )
    .reset_index()
)

# ------------------------------------------------------------
# 3. Transaction count
# ------------------------------------------------------------

transaction_features = (
    df.groupby("client_id")
    .agg(
        TRANSACTION_COUNT=("amount", "size"),
        AVG_TRANSACTION_AMOUNT=("amount", "mean"),
        STD_TRANSACTION_AMOUNT=("amount", "std"),
        MIN_TRANSACTION_AMOUNT=("amount", "min"),
        MAX_TRANSACTION_AMOUNT=("amount", "max"),
        TOTAL_TRANSACTION_AMOUNT=("amount", "sum"),
    )
    .reset_index()
)

# ------------------------------------------------------------
# 4. Transaction frequency
# ------------------------------------------------------------

date_features = (
    df.groupby("client_id")
    .agg(
        FIRST_TRANSACTION_DATE=("date", "min"),
        LAST_TRANSACTION_DATE=("date", "max"),
    )
    .reset_index()
)

date_features["TRANSACTION_HISTORY_DAYS"] = (
    date_features["LAST_TRANSACTION_DATE"]
    - date_features["FIRST_TRANSACTION_DATE"]
).dt.days

# ------------------------------------------------------------
# 5. Digital transaction behavior
# ------------------------------------------------------------

digital = (
    df.assign(
        DIGITAL_TRANSACTION=(
            df["use_chip"] == "Yes"
        ).astype(int)
    )
    .groupby("client_id")
    .agg(
        DIGITAL_TRANSACTION_COUNT=(
            "DIGITAL_TRANSACTION",
            "sum"
        )
    )
    .reset_index()
)

digital["DIGITAL_TRANSACTION_RATIO"] = (
    digital["DIGITAL_TRANSACTION_COUNT"]
    / transaction_features["TRANSACTION_COUNT"]
)

# ------------------------------------------------------------
# 6. Merchant diversity
# ------------------------------------------------------------

merchant_features = (
    df.groupby("client_id")
    .agg(
        UNIQUE_MERCHANTS=("merchant_id", "nunique"),
        UNIQUE_MERCHANT_CITIES=(
            "merchant_city",
            "nunique"
        ),
        UNIQUE_MERCHANT_STATES=(
            "merchant_state",
            "nunique"
        ),
    )
    .reset_index()
)

# ------------------------------------------------------------
# 7. Spending concentration
# ------------------------------------------------------------

spending = (
    df.groupby("client_id")
    .agg(
        HIGH_VALUE_TRANSACTION_COUNT=(
            "amount",
            lambda x: (x > 5000).sum()
        ),
        VERY_HIGH_VALUE_TRANSACTION_COUNT=(
            "amount",
            lambda x: (x > 10000).sum()
        ),
    )
    .reset_index()
)

spending["HIGH_VALUE_TRANSACTION_RATIO"] = (
    spending["HIGH_VALUE_TRANSACTION_COUNT"]
    / transaction_features["TRANSACTION_COUNT"]
)

spending["VERY_HIGH_VALUE_TRANSACTION_RATIO"] = (
    spending["VERY_HIGH_VALUE_TRANSACTION_COUNT"]
    / transaction_features["TRANSACTION_COUNT"]
)

# ------------------------------------------------------------
# 8. Monthly transaction behavior
# ------------------------------------------------------------

df["YEAR_MONTH"] = df["date"].dt.to_period("M")

monthly = (
    df.groupby(
        ["client_id", "YEAR_MONTH"]
    )
    .agg(
        MONTHLY_SPENDING=("amount", "sum"),
        MONTHLY_TRANSACTION_COUNT=(
            "amount",
            "size"
        )
    )
    .reset_index()
)

monthly_features = (
    monthly.groupby("client_id")
    .agg(
        AVG_MONTHLY_SPENDING=(
            "MONTHLY_SPENDING",
            "mean"
        ),
        STD_MONTHLY_SPENDING=(
            "MONTHLY_SPENDING",
            "std"
        ),
        MAX_MONTHLY_SPENDING=(
            "MONTHLY_SPENDING",
            "max"
        ),
        AVG_MONTHLY_TRANSACTION_COUNT=(
            "MONTHLY_TRANSACTION_COUNT",
            "mean"
        ),
    )
    .reset_index()
)

# ------------------------------------------------------------
# 9. Financial ratios
# ------------------------------------------------------------

client["DEBT_TO_INCOME_RATIO"] = np.where(
    client["YEARLY_INCOME"] > 0,
    client["TOTAL_DEBT"]
    / client["YEARLY_INCOME"],
    np.nan
)

client["CREDIT_SCORE_NORMALIZED"] = (
    client["CREDIT_SCORE"] / 900.0
)

# ------------------------------------------------------------
# 10. Merge all features
# ------------------------------------------------------------

result = client.copy()

feature_tables = [
    transaction_features,
    date_features[
        [
            "client_id",
            "TRANSACTION_HISTORY_DAYS"
        ]
    ],
    digital,
    merchant_features,
    spending,
    monthly_features,
]

for table in feature_tables:

    result = result.merge(
        table,
        on="client_id",
        how="left"
    )

# ------------------------------------------------------------
# 11. Remove raw dates
# ------------------------------------------------------------

result = result.drop(
    columns=[
        col
        for col in result.columns
        if "DATE" in col
    ],
    errors="ignore"
)

# ------------------------------------------------------------
# 12. Handle standard deviation for single transactions
# ------------------------------------------------------------

result[
    [
        "STD_TRANSACTION_AMOUNT",
        "STD_MONTHLY_SPENDING"
    ]
] = result[
    [
        "STD_TRANSACTION_AMOUNT",
        "STD_MONTHLY_SPENDING"
    ]
].fillna(0)

# ------------------------------------------------------------
# 13. Save
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    OUTPUT,
    index=False
)

# ------------------------------------------------------------
# 14. Report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("INDIAN ALTERNATIVE FEATURES CREATED")
print("=" * 70)

print(
    "Clients:",
    len(result)
)

print(
    "Features:",
    len(result.columns)
)

print("\nFeature columns:")

for col in result.columns:
    print("-", col)

print("\nMissing values:")

missing = (
    result.isnull()
    .sum()
    .sort_values(
        ascending=False
    )
)

print(
    missing[missing > 0]
)

print("\nFirst 5 clients:")

print(
    result.head().to_string(
        index=False
    )
)

print("\nSaved to:")

print(OUTPUT)

print("\n" + "=" * 70)
print("FEATURE ENGINEERING COMPLETED")
print("=" * 70)