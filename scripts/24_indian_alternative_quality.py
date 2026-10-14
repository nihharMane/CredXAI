import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - INDIAN ALTERNATIVE FEATURE QUALITY CHECK
# ============================================================

INPUT = Path(
    "data/processed/indian_alternative_features.csv"
)

print("=" * 70)
print("CREDXAI - INDIAN ALTERNATIVE FEATURE QUALITY CHECK")
print("=" * 70)

df = pd.read_csv(INPUT)

# ------------------------------------------------------------
# 1. Dataset
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DATASET")
print("=" * 70)

print("Rows:", len(df))
print("Columns:", len(df.columns))

print(
    "Unique clients:",
    df["client_id"].nunique()
)

# ------------------------------------------------------------
# 2. Duplicate clients
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DUPLICATE CLIENTS")
print("=" * 70)

print(
    "Duplicate client IDs:",
    df["client_id"].duplicated().sum()
)

# ------------------------------------------------------------
# 3. Missing values
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

if missing.sum() == 0:
    print("No missing values.")

else:
    print(
        missing[missing > 0]
    )

# ------------------------------------------------------------
# 4. Infinite values
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("INFINITE VALUES")
print("=" * 70)

numeric = df.select_dtypes(
    include=["number"]
)

infinite_count = np.isinf(
    numeric
).sum().sum()

print(
    "Total infinite values:",
    infinite_count
)

# ------------------------------------------------------------
# 5. Numeric summary
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("NUMERIC FEATURE SUMMARY")
print("=" * 70)

print(
    numeric.describe()
    .T
    .to_string()
)

# ------------------------------------------------------------
# 6. Impossible values
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("LOGICAL VALUE CHECKS")
print("=" * 70)

checks = {
    "AGE < 18": (
        df["AGE"] < 18
    ).sum(),

    "AGE > 100": (
        df["AGE"] > 100
    ).sum(),

    "YEARLY_INCOME <= 0": (
        df["YEARLY_INCOME"] <= 0
    ).sum(),

    "TOTAL_DEBT < 0": (
        df["TOTAL_DEBT"] < 0
    ).sum(),

    "CREDIT_SCORE < 300": (
        df["CREDIT_SCORE"] < 300
    ).sum(),

    "CREDIT_SCORE > 900": (
        df["CREDIT_SCORE"] > 900
    ).sum(),

    "NUM_CREDIT_CARDS < 0": (
        df["NUM_CREDIT_CARDS"] < 0
    ).sum(),

    "TRANSACTION_COUNT <= 0": (
        df["TRANSACTION_COUNT"] <= 0
    ).sum(),

    "DEBT_TO_INCOME < 0": (
        df["DEBT_TO_INCOME_RATIO"] < 0
    ).sum(),

    "DIGITAL_RATIO < 0": (
        df["DIGITAL_TRANSACTION_RATIO"] < 0
    ).sum(),

    "DIGITAL_RATIO > 1": (
        df["DIGITAL_TRANSACTION_RATIO"] > 1
    ).sum(),

    "HIGH_VALUE_RATIO < 0": (
        df["HIGH_VALUE_TRANSACTION_RATIO"] < 0
    ).sum(),

    "HIGH_VALUE_RATIO > 1": (
        df["HIGH_VALUE_TRANSACTION_RATIO"] > 1
    ).sum(),
}

for name, count in checks.items():

    print(
        f"{name:<30}: {count}"
    )

# ------------------------------------------------------------
# 7. Constant features
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CONSTANT FEATURES")
print("=" * 70)

constant = []

for col in numeric.columns:

    if df[col].nunique() <= 1:
        constant.append(col)

print(
    "Count:",
    len(constant)
)

for col in constant:
    print("-", col)

# ------------------------------------------------------------
# 8. Highly correlated features
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("HIGH CORRELATION")
print("=" * 70)

corr = numeric.corr().abs()

pairs = []

for i in range(len(corr.columns)):

    for j in range(i + 1, len(corr.columns)):

        value = corr.iloc[i, j]

        if value >= 0.90:

            pairs.append(
                (
                    corr.columns[i],
                    corr.columns[j],
                    value
                )
            )

pairs.sort(
    key=lambda x: x[2],
    reverse=True
)

if pairs:

    for a, b, value in pairs[:30]:

        print(
            f"{a} <-> {b}: {value:.4f}"
        )

else:

    print(
        "No correlations above 0.90."
    )

# ------------------------------------------------------------
# 9. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("QUALITY CHECK COMPLETED")
print("=" * 70)