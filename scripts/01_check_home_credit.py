import pandas as pd
from pathlib import Path

# ============================================================
# CredXAI - Home Credit Dataset Check
# ============================================================

DATA_DIR = Path("data/raw/home_credit")

FILES = {
    "application_train": "application_train.csv",
    "bureau": "bureau.csv",
    "credit_card_balance": "credit_card_balance.csv",
    "installments_payments": "installments_payments.csv",
    "POS_CASH_balance": "POS_CASH_balance.csv",
    "previous_application": "previous_application.csv",
}

print("=" * 70)
print("CREDXAI - HOME CREDIT DATA CHECK")
print("=" * 70)

for name, filename in FILES.items():

    path = DATA_DIR / filename

    print("\n" + "=" * 70)
    print(f"{name.upper()}")
    print("=" * 70)

    if not path.exists():
        print("ERROR: File not found:", path)
        continue

    # Read only 5 rows so we don't load huge files unnecessarily
    sample = pd.read_csv(path, nrows=5)

    print("File:", path)
    print("Sample rows:", len(sample))
    print("Number of columns:", len(sample.columns))

    print("\nColumns:")
    print(sample.columns.tolist())

    print("\nFirst row:")
    print(sample.iloc[0].to_dict())

print("\n" + "=" * 70)
print("DATA CHECK COMPLETED")
print("=" * 70)