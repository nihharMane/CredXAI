import pandas as pd
import json
from pathlib import Path

# ============================================================
# CREDXAI
# ELECTRIC SHEEP ALTERNATIVE DATA INSPECTION
# ============================================================

BASE = Path(
    "data/external/electric_sheep_india"
)

PROFILE_PATH = BASE / "credit_profiles.parquet"
TRANSACTION_PATH = BASE / "transactions_IN.parquet"
METADATA_PATH = BASE / "metadata.json"

print("=" * 70)
print("CREDXAI - ALTERNATIVE DATA INSPECTION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Credit profiles
# ------------------------------------------------------------

profiles = pd.read_parquet(PROFILE_PATH)

print("\n" + "=" * 70)
print("CREDIT PROFILES")
print("=" * 70)

print("Shape:", profiles.shape)

print("\nColumns:")
for column in profiles.columns:
    print("-", column)

print("\nCredit outcome:")
print(
    profiles["credit_outcome"]
    .value_counts(dropna=False)
)

print("\nRisk bucket:")
print(
    profiles["risk_bucket"]
    .value_counts(dropna=False)
)

# ------------------------------------------------------------
# 2. Transactions
# ------------------------------------------------------------

transactions = pd.read_parquet(
    TRANSACTION_PATH
)

print("\n" + "=" * 70)
print("TRANSACTIONS")
print("=" * 70)

print("Shape:", transactions.shape)

print("\nColumns:")
for column in transactions.columns:
    print("-", column)

print("\nUnique users:")
print(
    transactions["user_id"].nunique()
)

print("\nTransaction date range:")

print(
    "Minimum:",
    transactions["timestamp"].min()
)

print(
    "Maximum:",
    transactions["timestamp"].max()
)

print("\nTransaction types:")
print(
    transactions["transaction_type"]
    .value_counts(dropna=False)
)

print("\nCategories:")
print(
    transactions["category"]
    .value_counts(dropna=False)
)

print("\nChannels:")
print(
    transactions["channel"]
    .value_counts(dropna=False)
)

# ------------------------------------------------------------
# 3. Match profiles and transactions
# ------------------------------------------------------------

profile_users = set(
    profiles["user_id"]
)

transaction_users = set(
    transactions["user_id"]
)

matched_users = (
    profile_users &
    transaction_users
)

print("\n" + "=" * 70)
print("USER MATCHING")
print("=" * 70)

print(
    "Profile users:",
    len(profile_users)
)

print(
    "Transaction users:",
    len(transaction_users)
)

print(
    "Users appearing in both:",
    len(matched_users)
)

# ------------------------------------------------------------
# 4. Profile target distribution
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PROFILE TARGET DISTRIBUTION")
print("=" * 70)

print(
    profiles[
        [
            "credit_outcome",
            "default_probability",
            "risk_bucket"
        ]
    ].to_string()
)

print("\nInspection completed.")