import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - PREPARE SIMPLE ALTERNATIVE MODEL DATA
# ============================================================

INPUT = Path(
    "data/processed/alternative_model_dataset.csv"
)

OUTPUT = Path(
    "data/processed/simple_alternative_model_dataset.csv"
)

print("=" * 70)
print("CREDXAI - SIMPLE ALTERNATIVE MODEL DATA")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load existing prepared dataset
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

print("\nOriginal dataset:")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 2. Select user-friendly features
# ------------------------------------------------------------

features = [
    "age_range",
    "account_tenure_days",
    "avg_monthly_income",
    "avg_monthly_spend",
    "avg_balance",
    "overdraft_frequency",
    "bill_payment_consistency",
    "cashflow_stability_score"
]

target = "TARGET"

required = features + [target, "user_id"]

missing = [
    col for col in required
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing columns: {missing}"
    )

simple_df = df[
    required
].copy()

# ------------------------------------------------------------
# 3. Remove missing values
# ------------------------------------------------------------

print("\nMissing values before cleaning:")

print(
    simple_df.isnull()
    .sum()
)

simple_df = simple_df.dropna()

# ------------------------------------------------------------
# 4. Validate
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL DATASET")
print("=" * 70)

print(
    "Rows:",
    len(simple_df)
)

print(
    "Columns:",
    len(simple_df.columns)
)

print("\nFeatures:")

for feature in features:
    print("-", feature)

print("\nTarget distribution:")

print(
    simple_df[target]
    .value_counts()
)

# ------------------------------------------------------------
# 5. Save
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

simple_df.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved to:")

print(OUTPUT)

print("\n" + "=" * 70)
print("SIMPLE ALTERNATIVE DATA PREPARATION COMPLETED")
print("=" * 70)