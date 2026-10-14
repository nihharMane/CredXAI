import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - PREPARE ALTERNATIVE MODEL DATA
# ============================================================

INPUT = Path(
    "data/external/electric_sheep_india/credit_profiles.parquet"
)

OUTPUT = Path(
    "data/processed/alternative_model_dataset.csv"
)

print("=" * 80)
print("CREDXAI - PREPARE ALTERNATIVE MODEL DATA")
print("=" * 80)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

print("\nLoading alternative credit profiles...")

df = pd.read_parquet(INPUT)

print("Original rows:", len(df))

# ------------------------------------------------------------
# 2. Inspect target
# ------------------------------------------------------------

print("\nOriginal target distribution:")

print(
    df["credit_outcome"]
    .value_counts(dropna=False)
)

# ------------------------------------------------------------
# 3. Remove indeterminate applicants
# ------------------------------------------------------------

print("\nRemoving indeterminate outcomes...")

df = df[
    df["credit_outcome"].isin(
        ["good", "bad"]
    )
].copy()

print(
    "Rows after filtering:",
    len(df)
)

print("\nTarget distribution:")

print(
    df["credit_outcome"]
    .value_counts()
)

# ------------------------------------------------------------
# 4. Create binary target
# ------------------------------------------------------------

df["TARGET"] = (
    df["credit_outcome"]
    .map({
        "good": 0,
        "bad": 1
    })
)

# ------------------------------------------------------------
# 5. Select alternative behavioral features
# ------------------------------------------------------------

FEATURES = [
    "age_range",
    "account_tenure_days",

    "avg_monthly_income",
    "income_volatility",
    "income_frequency",
    "income_trend",
    "income_gap_months",

    "avg_monthly_spend",
    "spending_volatility",
    "essential_spend_ratio",
    "discretionary_spend_ratio",
    "betting_ratio",

    "avg_balance",
    "min_balance",
    "max_balance",
    "overdraft_frequency",

    "bill_payment_consistency",
    "recurring_expense_ratio",

    "transaction_frequency",
    "cashflow_stability_score"
]

# ------------------------------------------------------------
# 6. Check available features
# ------------------------------------------------------------

available_features = [
    col
    for col in FEATURES
    if col in df.columns
]

missing_features = [
    col
    for col in FEATURES
    if col not in df.columns
]

print("\nSelected features:")

for col in available_features:
    print("-", col)

if missing_features:

    print("\nWARNING - Missing features:")

    for col in missing_features:
        print("-", col)

# ------------------------------------------------------------
# 7. Create final dataset
# ------------------------------------------------------------

model_df = df[
    ["user_id", "credit_outcome", "TARGET"]
    + available_features
].copy()

# ------------------------------------------------------------
# 8. Handle missing numeric values
# ------------------------------------------------------------

numeric_features = model_df[
    available_features
].select_dtypes(
    include=["number"]
).columns

for col in numeric_features:

    model_df[col] = (
        model_df[col]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )

    model_df[col] = (
        model_df[col]
        .fillna(
            model_df[col].median()
        )
    )

# ------------------------------------------------------------
# 9. Convert age_range if required
# ------------------------------------------------------------

if "age_range" in model_df.columns:

    print(
        "\nAge range values:"
    )

    print(
        model_df["age_range"]
        .value_counts()
    )

# ------------------------------------------------------------
# 10. Final validation
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("FINAL DATASET VALIDATION")
print("=" * 80)

print(
    "Rows:",
    len(model_df)
)

print(
    "Columns:",
    len(model_df.columns)
)

print(
    "Missing values:",
    model_df.isnull().sum().sum()
)

print(
    "Duplicate users:",
    model_df["user_id"].duplicated().sum()
)

print("\nTarget distribution:")

print(
    model_df["TARGET"]
    .value_counts()
)

# ------------------------------------------------------------
# 11. Verify leakage columns are excluded
# ------------------------------------------------------------

LEAKAGE_COLUMNS = [
    "default_probability",
    "risk_behavior_score"
]

print("\nLeakage columns excluded:")

for col in LEAKAGE_COLUMNS:

    print(
        f"{col}:",
        col not in model_df.columns
    )

# ------------------------------------------------------------
# 12. Save
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

model_df.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved to:")

print(OUTPUT)

print("\n" + "=" * 80)
print("ALTERNATIVE MODEL DATA PREPARATION COMPLETED")
print("=" * 80)