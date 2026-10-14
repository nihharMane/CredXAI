import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - INDIAN ALTERNATIVE DATA INSPECTION
# ============================================================

INPUT = Path(
    "data/external/Customer_financial_profiles.csv"
)

print("=" * 70)
print("CREDXAI - INDIAN ALTERNATIVE DATA INSPECTION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load
# ------------------------------------------------------------

print("\nLoading Indian financial dataset...")

df = pd.read_csv(INPUT)

print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 2. Unique entities
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("UNIQUE ENTITIES")
print("=" * 70)

print(
    "Unique clients:",
    df["client_id"].nunique()
)

print(
    "Unique cards:",
    df["card_id"].nunique()
)

print(
    "Unique transactions:",
    df["transaction_id"].nunique()
)

print(
    "Unique merchants:",
    df["merchant_id"].nunique()
)

# ------------------------------------------------------------
# 3. Transactions per client
# ------------------------------------------------------------

transactions_per_client = (
    df.groupby("client_id")
    .size()
)

print("\n" + "=" * 70)
print("TRANSACTIONS PER CLIENT")
print("=" * 70)

print(
    transactions_per_client.describe()
)

# ------------------------------------------------------------
# 4. Client consistency
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CLIENT-LEVEL FIELD CONSISTENCY")
print("=" * 70)

client_fields = [
    "current_age",
    "gender",
    "per_capita_income",
    "yearly_income",
    "total_debt",
    "credit_score",
    "num_credit_cards"
]

for col in client_fields:

    counts = (
        df.groupby("client_id")[col]
        .nunique(dropna=False)
    )

    inconsistent = (
        counts > 1
    ).sum()

    print(
        f"{col:<22} "
        f"inconsistent clients: {inconsistent}"
    )

# ------------------------------------------------------------
# 5. Transaction amount
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRANSACTION AMOUNT")
print("=" * 70)

print(
    df["amount"].describe()
)

print(
    "\nNegative amounts:",
    (df["amount"] < 0).sum()
)

print(
    "Positive amounts:",
    (df["amount"] > 0).sum()
)

print(
    "Zero amounts:",
    (df["amount"] == 0).sum()
)

# ------------------------------------------------------------
# 6. Transaction channels
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRANSACTION CHANNEL")
print("=" * 70)

print(
    df["use_chip"]
    .value_counts(dropna=False)
)

# ------------------------------------------------------------
# 7. Merchant locations
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MERCHANT LOCATIONS")
print("=" * 70)

print(
    "Cities:",
    df["merchant_city"].nunique()
)

print(
    "States:",
    df["merchant_state"].nunique()
)

print("\nTop states:")

print(
    df["merchant_state"]
    .value_counts()
    .head(15)
)

# ------------------------------------------------------------
# 8. Date
# ------------------------------------------------------------

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

print("\n" + "=" * 70)
print("DATE RANGE")
print("=" * 70)

print(
    "Minimum:",
    df["date"].min()
)

print(
    "Maximum:",
    df["date"].max()
)

# ------------------------------------------------------------
# 9. Missing values
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

missing = (
    df.isnull()
    .sum()
    .sort_values(
        ascending=False
    )
)

print(
    missing[missing > 0]
)

# ------------------------------------------------------------
# 10. Duplicate transactions
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATES")
print("=" * 70)

print(
    "Duplicate transaction IDs:",
    df["transaction_id"].duplicated().sum()
)

# ------------------------------------------------------------
# 11. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("INSPECTION COMPLETED")
print("=" * 70)