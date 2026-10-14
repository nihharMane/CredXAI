import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - ALTERNATIVE MODEL DATA INSPECTION
# ============================================================

PROFILE_PATH = Path(
    "data/external/electric_sheep_india/credit_profiles.parquet"
)

TRANSACTION_PATH = Path(
    "data/external/electric_sheep_india/transactions_IN.parquet"
)

print("=" * 80)
print("CREDXAI - ALTERNATIVE MODEL DATA INSPECTION")
print("=" * 80)

# ------------------------------------------------------------
# 1. Load profile data
# ------------------------------------------------------------

print("\nLoading credit profiles...")

profiles = pd.read_parquet(PROFILE_PATH)

print("Profile rows:", len(profiles))
print("Profile columns:", len(profiles.columns))

print("\nProfile columns:")
for col in profiles.columns:
    print("-", col)

# ------------------------------------------------------------
# 2. Basic profile information
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("PROFILE DATA TYPES")
print("=" * 80)

print(profiles.dtypes.to_string())

# ------------------------------------------------------------
# 3. Missing values
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("PROFILE MISSING VALUES")
print("=" * 80)

missing = profiles.isnull().sum()

print(
    missing[missing > 0]
    .sort_values(ascending=False)
    .to_string()
)

# ------------------------------------------------------------
# 4. Target inspection
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TARGET INSPECTION")
print("=" * 80)

possible_targets = [
    "credit_outcome",
    "default_probability",
    "default",
    "target",
    "loan_default",
    "risk"
]

for column in possible_targets:

    if column in profiles.columns:

        print(f"\nFOUND: {column}")

        print(
            "Data type:",
            profiles[column].dtype
        )

        print(
            "Unique values:",
            profiles[column].nunique()
        )

        print(
            profiles[column]
            .value_counts(dropna=False)
            .head(20)
            .to_string()
        )

# ------------------------------------------------------------
# 5. Unique users
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("USER INFORMATION")
print("=" * 80)

if "user_id" in profiles.columns:

    print(
        "Unique profile users:",
        profiles["user_id"].nunique()
    )

    print(
        "Duplicate user IDs:",
        profiles["user_id"].duplicated().sum()
    )

# ------------------------------------------------------------
# 6. Load transactions
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TRANSACTION DATA")
print("=" * 80)

transactions = pd.read_parquet(
    TRANSACTION_PATH
)

print(
    "Transaction rows:",
    len(transactions)
)

print(
    "Transaction columns:",
    len(transactions.columns)
)

print("\nTransaction columns:")

for col in transactions.columns:
    print("-", col)

# ------------------------------------------------------------
# 7. Transaction users
# ------------------------------------------------------------

if "user_id" in transactions.columns:

    print(
        "\nUnique transaction users:",
        transactions["user_id"].nunique()
    )

    print(
        "Duplicate transaction rows:",
        transactions.duplicated().sum()
    )

# ------------------------------------------------------------
# 8. Transaction missing values
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TRANSACTION MISSING VALUES")
print("=" * 80)

transaction_missing = (
    transactions.isnull()
    .sum()
)

print(
    transaction_missing[
        transaction_missing > 0
    ]
    .sort_values(ascending=False)
    .to_string()
)

# ------------------------------------------------------------
# 9. Numeric summary
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("PROFILE NUMERIC SUMMARY")
print("=" * 80)

numeric_profiles = profiles.select_dtypes(
    include="number"
)

print(
    numeric_profiles.describe()
    .T
    .to_string()
)

# ------------------------------------------------------------
# 10. Transaction numeric summary
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TRANSACTION NUMERIC SUMMARY")
print("=" * 80)

numeric_transactions = transactions.select_dtypes(
    include="number"
)

print(
    numeric_transactions.describe()
    .T
    .to_string()
)

# ------------------------------------------------------------
# 11. Final
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("INSPECTION COMPLETED")
print("=" * 80)