import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - DUPLICATE TRANSACTION INVESTIGATION
# ============================================================

INPUT = Path(
    "data/external/Customer_financial_profiles.csv"
)

print("=" * 70)
print("CREDXAI - DUPLICATE TRANSACTION INVESTIGATION")
print("=" * 70)

df = pd.read_csv(INPUT)

# ------------------------------------------------------------
# 1. Duplicate transaction IDs
# ------------------------------------------------------------

duplicate_counts = (
    df.groupby("transaction_id")
    .size()
    .sort_values(ascending=False)
)

duplicates = duplicate_counts[
    duplicate_counts > 1
]

print("\nTotal transaction IDs:", df["transaction_id"].nunique())

print(
    "Transaction IDs appearing more than once:",
    len(duplicates)
)

print(
    "Rows belonging to duplicate IDs:",
    duplicates.sum()
)

# ------------------------------------------------------------
# 2. Most duplicated transaction IDs
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MOST DUPLICATED TRANSACTION IDs")
print("=" * 70)

print(
    duplicate_counts.head(20)
)

# ------------------------------------------------------------
# 3. Show examples
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EXAMPLE DUPLICATE RECORDS")
print("=" * 70)

example_ids = duplicates.head(5).index

for transaction_id in example_ids:

    print("\nTransaction ID:", transaction_id)

    cols = [
        "transaction_id",
        "client_id",
        "card_id",
        "date",
        "amount",
        "use_chip",
        "merchant_id",
        "merchant_city",
        "merchant_state"
    ]

    print(
        df[
            df["transaction_id"] == transaction_id
        ][cols].to_string(index=False)
    )

# ------------------------------------------------------------
# 4. Are duplicate rows completely identical?
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EXACT DUPLICATES")
print("=" * 70)

exact_duplicate_rows = df.duplicated(
    keep=False
)

print(
    "Rows that are exact duplicates:",
    exact_duplicate_rows.sum()
)

print(
    "Unique rows after removing exact duplicates:",
    len(df.drop_duplicates())
)

# ------------------------------------------------------------
# 5. Duplicate transaction across clients
# ------------------------------------------------------------

transaction_client_count = (
    df.groupby("transaction_id")["client_id"]
    .nunique()
)

cross_client = transaction_client_count[
    transaction_client_count > 1
]

print("\n" + "=" * 70)
print("TRANSACTION IDs USED BY MULTIPLE CLIENTS")
print("=" * 70)

print(
    "Count:",
    len(cross_client)
)

if len(cross_client) > 0:
    print(
        cross_client.head(20)
    )

# ------------------------------------------------------------
# 6. Duplicate transaction across dates
# ------------------------------------------------------------

transaction_date_count = (
    df.groupby("transaction_id")["date"]
    .nunique()
)

multi_date = transaction_date_count[
    transaction_date_count > 1
]

print("\n" + "=" * 70)
print("TRANSACTION IDs WITH MULTIPLE DATES")
print("=" * 70)

print(
    "Count:",
    len(multi_date)
)

# ------------------------------------------------------------
# 7. Duplicate transaction across amounts
# ------------------------------------------------------------

transaction_amount_count = (
    df.groupby("transaction_id")["amount"]
    .nunique()
)

multi_amount = transaction_amount_count[
    transaction_amount_count > 1
]

print("\n" + "=" * 70)
print("TRANSACTION IDs WITH MULTIPLE AMOUNTS")
print("=" * 70)

print(
    "Count:",
    len(multi_amount)
)

# ------------------------------------------------------------
# 8. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATE INVESTIGATION COMPLETED")
print("=" * 70)