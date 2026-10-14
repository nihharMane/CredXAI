import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - FINAL DATASET CONSTRUCTION
# ============================================================

BASE = Path("data/processed")

OUTPUT = BASE / "final_home_credit_dataset.csv"

print("=" * 70)
print("CREDXAI - FINAL DATASET CONSTRUCTION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load application features
# ------------------------------------------------------------

print("\nLoading application features...")

final_df = pd.read_csv(
    BASE / "application_features.csv"
)

print("Initial rows:", len(final_df))
print("Initial columns:", len(final_df.columns))

# Make sure applicant ID is unique
assert final_df["SK_ID_CURR"].is_unique

# ------------------------------------------------------------
# 2. Historical feature files
# ------------------------------------------------------------

feature_files = [
    (
        "previous_application_features.csv",
        "Previous applications"
    ),
    (
        "installment_features.csv",
        "Installment history"
    ),
    (
        "credit_card_features.csv",
        "Credit-card history"
    ),
    (
        "pos_cash_features.csv",
        "POS/Cash history"
    ),
    (
        "bureau_features.csv",
        "Bureau history"
    )
]

# ------------------------------------------------------------
# 3. Merge each dataset
# ------------------------------------------------------------

for filename, name in feature_files:

    print("\n" + "-" * 70)
    print("Merging:", name)

    path = BASE / filename

    df = pd.read_csv(path)

    print("Rows:", len(df))
    print(
        "Unique applicants:",
        df["SK_ID_CURR"].nunique()
    )

    # Each feature file must contain one row per applicant
    if not df["SK_ID_CURR"].is_unique:
        raise ValueError(
            f"{name} contains duplicate SK_ID_CURR values."
        )

    before = len(final_df)

    final_df = final_df.merge(
        df,
        on="SK_ID_CURR",
        how="left",
        validate="one_to_one"
    )

    after = len(final_df)

    print("Rows before merge:", before)
    print("Rows after merge:", after)

    # A LEFT JOIN must not change applicant count
    if before != after:
        raise ValueError(
            f"Applicant count changed while merging {name}."
        )

# ------------------------------------------------------------
# 4. Final shape
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL DATASET CHECK")
print("=" * 70)

print("Rows:", len(final_df))
print("Columns:", len(final_df.columns))

print(
    "Unique applicants:",
    final_df["SK_ID_CURR"].nunique()
)

# ------------------------------------------------------------
# 5. Target check
# ------------------------------------------------------------

print("\nTARGET distribution:")

print(
    final_df["TARGET"].value_counts()
)

print("\nTARGET percentage:")

print(
    (
        final_df["TARGET"]
        .value_counts(normalize=True)
        * 100
    ).round(2)
)

# ------------------------------------------------------------
# 6. Historical-data availability
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("HISTORICAL DATA AVAILABILITY")
print("=" * 70)

history_columns = {
    "Previous applications":
        "PREVIOUS_APPLICATION_COUNT",

    "Installments":
        "INSTALLMENT_COUNT",

    "Credit cards":
        "CREDIT_CARD_RECORD_COUNT",

    "POS/Cash":
        "POS_CASH_RECORD_COUNT",

    "Bureau":
        "BUREAU_CREDIT_COUNT"
}

for name, column in history_columns.items():

    with_history = final_df[column].notna().sum()
    without_history = final_df[column].isna().sum()

    print(
        f"{name}: "
        f"{with_history:,} with history | "
        f"{without_history:,} without history"
    )

# ------------------------------------------------------------
# 7. Missing-value summary
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

missing = (
    final_df.isnull()
    .sum()
    .sort_values(ascending=False)
)

missing = missing[missing > 0]

print(
    "Columns containing missing values:",
    len(missing)
)

print("\nTop 30:")
print(
    missing.head(30).to_string()
)

# ------------------------------------------------------------
# 8. Save
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

final_df.to_csv(
    OUTPUT,
    index=False
)

print("\n" + "=" * 70)
print("FINAL DATASET SAVED")
print("=" * 70)

print("Path:")
print(OUTPUT)

print("\nShape:")
print(final_df.shape)

print("\nCompleted successfully.")
print("=" * 70)