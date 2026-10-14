import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - ALTERNATIVE DATA FEATURE ENGINEERING
# ============================================================

PROFILE_FILE = Path(
    "data/external/electric_sheep_india/credit_profiles.parquet"
)

TRANSACTION_FILE = Path(
    "data/external/electric_sheep_india/transactions_IN.parquet"
)

OUTPUT_FILE = Path(
    "data/processed/alternative_features.csv"
)

print("=" * 70)
print("CREDXAI - ALTERNATIVE DATA FEATURE ENGINEERING")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

print("\nLoading credit profiles...")

profiles = pd.read_parquet(
    PROFILE_FILE
)

print(
    "Profile rows:",
    len(profiles)
)

print("\nLoading transactions...")

transactions = pd.read_parquet(
    TRANSACTION_FILE
)

print(
    "Transaction rows:",
    len(transactions)
)

# ------------------------------------------------------------
# 2. Prepare transaction data
# ------------------------------------------------------------

transactions["timestamp"] = pd.to_datetime(
    transactions["timestamp"]
)

transactions["amount"] = pd.to_numeric(
    transactions["amount"],
    errors="coerce"
)

transactions["month"] = (
    transactions["timestamp"]
    .dt.to_period("M")
)

# ------------------------------------------------------------
# 3. Basic transaction features
# ------------------------------------------------------------

print("\nCreating transaction features...")

grouped = transactions.groupby(
    "user_id"
)

features = grouped.agg(
    TRANSACTION_COUNT=(
        "transaction_id",
        "count"
    ),

    AVG_TRANSACTION_AMOUNT=(
        "amount",
        "mean"
    ),

    TRANSACTION_AMOUNT_STD=(
        "amount",
        "std"
    ),

    AVG_BALANCE=(
        "balance_estimate",
        "mean"
    ),

    MIN_BALANCE=(
        "balance_estimate",
        "min"
    ),

    MAX_BALANCE=(
        "balance_estimate",
        "max"
    )
).reset_index()

# ------------------------------------------------------------
# 4. Credit / debit behavior
# ------------------------------------------------------------

credit = (
    transactions[
        transactions["transaction_type"]
        == "credit"
    ]
    .groupby("user_id")["amount"]
    .agg(
        TOTAL_INCOME="sum",
        INCOME_COUNT="count"
    )
    .reset_index()
)

debit = (
    transactions[
        transactions["transaction_type"]
        == "debit"
    ]
    .assign(
        debit_amount=lambda x:
        x["amount"].abs()
    )
    .groupby("user_id")["debit_amount"]
    .agg(
        TOTAL_SPENDING="sum",
        SPENDING_COUNT="count"
    )
    .reset_index()
)

features = features.merge(
    credit,
    on="user_id",
    how="left"
)

features = features.merge(
    debit,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 5. Monthly income and spending
# ------------------------------------------------------------

monthly_income = (
    transactions[
        transactions["transaction_type"]
        == "credit"
    ]
    .assign(
        income=lambda x:
        x["amount"].abs()
    )
    .groupby(
        ["user_id", "month"]
    )["income"]
    .sum()
    .reset_index()
)

monthly_spending = (
    transactions[
        transactions["transaction_type"]
        == "debit"
    ]
    .assign(
        spending=lambda x:
        x["amount"].abs()
    )
    .groupby(
        ["user_id", "month"]
    )["spending"]
    .sum()
    .reset_index()
)

monthly_income_features = (
    monthly_income
    .groupby("user_id")["income"]
    .agg(
        AVG_MONTHLY_INCOME="mean",
        INCOME_VOLATILITY="std"
    )
    .reset_index()
)

monthly_spending_features = (
    monthly_spending
    .groupby("user_id")["spending"]
    .agg(
        AVG_MONTHLY_SPENDING="mean",
        SPENDING_VOLATILITY="std"
    )
    .reset_index()
)

features = features.merge(
    monthly_income_features,
    on="user_id",
    how="left"
)

features = features.merge(
    monthly_spending_features,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 6. Bills
# ------------------------------------------------------------

bill_features = (
    transactions[
        transactions["category"]
        == "bills"
    ]
    .groupby("user_id")
    .agg(
        BILL_PAYMENT_COUNT=(
            "transaction_id",
            "count"
        ),

        BILL_PAYMENT_AMOUNT=(
            "amount",
            lambda x: x.abs().sum()
        )
    )
    .reset_index()
)

features = features.merge(
    bill_features,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 7. Essential spending
# ------------------------------------------------------------

essential_categories = [
    "food",
    "transport",
    "bills",
    "healthcare"
]

essential = transactions[
    transactions["category"]
    .isin(essential_categories)
]

essential_features = (
    essential
    .assign(
        amount_abs=lambda x:
        x["amount"].abs()
    )
    .groupby("user_id")["amount_abs"]
    .sum()
    .reset_index(
        name="ESSENTIAL_SPENDING"
    )
)

features = features.merge(
    essential_features,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 8. Savings behavior
# ------------------------------------------------------------

savings_features = (
    transactions[
        transactions["category"]
        == "savings"
    ]
    .groupby("user_id")
    .agg(
        SAVINGS_TRANSACTION_COUNT=(
            "transaction_id",
            "count"
        ),

        SAVINGS_AMOUNT=(
            "amount",
            lambda x: x.abs().sum()
        )
    )
    .reset_index()
)

features = features.merge(
    savings_features,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 9. Recurring transactions
# ------------------------------------------------------------

recurring_features = (
    transactions[
        transactions["is_recurring"]
        == True
    ]
    .groupby("user_id")
    .agg(
        RECURRING_TRANSACTION_COUNT=(
            "transaction_id",
            "count"
        ),

        RECURRING_AMOUNT=(
            "amount",
            lambda x: x.abs().sum()
        )
    )
    .reset_index()
)

features = features.merge(
    recurring_features,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 10. Betting / risky spending
# ------------------------------------------------------------

betting_features = (
    transactions[
        transactions["category"]
        == "betting"
    ]
    .groupby("user_id")
    .agg(
        BETTING_TRANSACTION_COUNT=(
            "transaction_id",
            "count"
        ),

        BETTING_AMOUNT=(
            "amount",
            lambda x: x.abs().sum()
        )
    )
    .reset_index()
)

features = features.merge(
    betting_features,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 11. Transaction channels
# ------------------------------------------------------------

mobile_features = (
    transactions[
        transactions["channel"]
        == "mobile_money"
    ]
    .groupby("user_id")
    .size()
    .reset_index(
        name="MOBILE_MONEY_COUNT"
    )
)

features = features.merge(
    mobile_features,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 12. Profile information
# ------------------------------------------------------------

profile_columns = [
    "user_id",
    "age_range",
    "income_type",
    "account_tenure_days",
    "income_frequency",
    "income_trend",
    "income_gap_months",
    "cashflow_stability_score",
    "risk_behavior_score"
]

profile_selected = profiles[
    profile_columns
].copy()

features = features.merge(
    profile_selected,
    on="user_id",
    how="left"
)

# ------------------------------------------------------------
# 13. Derived ratios
# ------------------------------------------------------------

features["ESSENTIAL_SPENDING_RATIO"] = (
    features["ESSENTIAL_SPENDING"]
    /
    features["TOTAL_SPENDING"].replace(
        0,
        np.nan
    )
)

features["BILL_PAYMENT_RATIO"] = (
    features["BILL_PAYMENT_COUNT"]
    /
    features["TRANSACTION_COUNT"].replace(
        0,
        np.nan
    )
)

features["RECURRING_PAYMENT_RATIO"] = (
    features["RECURRING_TRANSACTION_COUNT"]
    /
    features["TRANSACTION_COUNT"].replace(
        0,
        np.nan
    )
)

features["SAVINGS_RATIO"] = (
    features["SAVINGS_AMOUNT"]
    /
    features["TOTAL_SPENDING"].replace(
        0,
        np.nan
    )
)

features["BETTING_RATIO"] = (
    features["BETTING_AMOUNT"]
    /
    features["TOTAL_SPENDING"].replace(
        0,
        np.nan
    )
)

features["SPENDING_TO_INCOME_RATIO"] = (
    features["TOTAL_SPENDING"]
    /
    features["TOTAL_INCOME"].replace(
        0,
        np.nan
    )
)

# ------------------------------------------------------------
# 14. Balance stress
# ------------------------------------------------------------

features["NEGATIVE_BALANCE_FLAG"] = (
    features["MIN_BALANCE"] < 0
).astype(int)

# ------------------------------------------------------------
# 15. Replace infinities
# ------------------------------------------------------------

features = features.replace(
    [np.inf, -np.inf],
    np.nan
)

# ------------------------------------------------------------
# 16. Fill count-based missing values
# ------------------------------------------------------------

count_columns = [
    "BILL_PAYMENT_COUNT",
    "SAVINGS_TRANSACTION_COUNT",
    "RECURRING_TRANSACTION_COUNT",
    "BETTING_TRANSACTION_COUNT",
    "MOBILE_MONEY_COUNT"
]

for col in count_columns:
    if col in features.columns:
        features[col] = features[col].fillna(0)

# ------------------------------------------------------------
# 17. Save
# ------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

features.to_csv(
    OUTPUT_FILE,
    index=False
)

# ------------------------------------------------------------
# 18. Summary
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ALTERNATIVE FEATURES CREATED")
print("=" * 70)

print(
    "Users:",
    len(features)
)

print(
    "Features:",
    len(features.columns)
)

print("\nFeature columns:")

for col in features.columns:
    print("-", col)

print("\nMissing values:")

print(
    features.isnull()
    .sum()
    .sort_values(
        ascending=False
    )
    .head(20)
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nAlternative feature engineering completed.")
print("=" * 70)