import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - DATA LEAKAGE CHECK
# ============================================================

INPUT = Path(
    "data/processed/final_home_credit_dataset.csv"
)

print("=" * 70)
print("CREDXAI - DATA LEAKAGE CHECK")
print("=" * 70)

df = pd.read_csv(INPUT)

print("\nDataset shape:")
print(df.shape)

print("\nTarget:")
print(df["TARGET"].value_counts())

# ------------------------------------------------------------
# 1. Check target-related columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TARGET-RELATED COLUMNS")
print("=" * 70)

target_related = [
    col for col in df.columns
    if "TARGET" in col.upper()
    or "DEFAULT" in col.upper()
    or "OUTCOME" in col.upper()
    or "REPAY" in col.upper()
]

for col in target_related:
    print("-", col)

# ------------------------------------------------------------
# 2. Check ID columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ID COLUMNS")
print("=" * 70)

id_columns = [
    col for col in df.columns
    if "ID" in col.upper()
]

for col in id_columns:
    print("-", col)

# ------------------------------------------------------------
# 3. Check suspicious columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SUSPICIOUS / POST-DECISION COLUMNS")
print("=" * 70)

suspicious_keywords = [
    "TARGET",
    "DEFAULT",
    "OUTCOME",
    "REPAY",
    "STATUS",
    "DAYS_DECISION",
    "DAYS_FIRST_DRAWING",
    "DAYS_FIRST_DUE",
    "DAYS_LAST_DUE",
    "DAYS_TERMINATION"
]

suspicious = []

for col in df.columns:

    col_upper = col.upper()

    for keyword in suspicious_keywords:

        if keyword in col_upper:

            suspicious.append(col)
            break

for col in sorted(set(suspicious)):

    print(
        f"{col}: "
        f"dtype={df[col].dtype}, "
        f"missing={df[col].isna().sum()}"
    )

# ------------------------------------------------------------
# 4. Check constant columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CONSTANT COLUMNS")
print("=" * 70)

constant_columns = []

for col in df.columns:

    if df[col].nunique(dropna=False) <= 1:

        constant_columns.append(col)

print(
    "Number of constant columns:",
    len(constant_columns)
)

print(constant_columns)

# ------------------------------------------------------------
# 5. Check duplicate rows
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATE CHECK")
print("=" * 70)

print(
    "Duplicate complete rows:",
    df.duplicated().sum()
)

print(
    "Duplicate applicant IDs:",
    df["SK_ID_CURR"].duplicated().sum()
)

# ------------------------------------------------------------
# 6. Check infinite values
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("INFINITE VALUES")
print("=" * 70)

numeric_df = df.select_dtypes(include="number")

infinite_count = (
    numeric_df.isin([float("inf"), float("-inf")])
    .sum()
    .sum()
)

print(
    "Total infinite values:",
    infinite_count
)

# ------------------------------------------------------------
# 7. Check target leakage through suspicious correlations
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("HIGH TARGET CORRELATIONS")
print("=" * 70)

correlations = (
    numeric_df.corr()["TARGET"]
    .drop("TARGET")
    .abs()
    .sort_values(ascending=False)
)

print(
    correlations.head(20).to_string()
)

# ------------------------------------------------------------
# 8. Final conclusion
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("LEAKAGE CHECK COMPLETED")
print("=" * 70)

print(
    """
IMPORTANT:
High correlation does NOT automatically mean leakage.

We will manually review suspicious columns
before training the Logistic Regression model.
"""
)

print("=" * 70)