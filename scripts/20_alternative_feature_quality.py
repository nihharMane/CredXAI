import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - ALTERNATIVE FEATURE QUALITY CHECK
# ============================================================

INPUT = Path(
    "data/processed/alternative_features.csv"
)

print("=" * 70)
print("CREDXAI - ALTERNATIVE FEATURE QUALITY CHECK")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

print("\nDataset shape:")
print(df.shape)

# ------------------------------------------------------------
# 2. Numeric summary
# ------------------------------------------------------------

numeric_columns = df.select_dtypes(
    include=["number"]
).columns.tolist()

print("\n" + "=" * 70)
print("NUMERIC FEATURE SUMMARY")
print("=" * 70)

print(
    df[numeric_columns]
    .describe()
    .T
    .to_string()
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

print(
    missing[missing > 0].to_string()
)

# ------------------------------------------------------------
# 4. Constant features
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CONSTANT FEATURES")
print("=" * 70)

constant_features = []

for col in numeric_columns:

    if df[col].nunique(dropna=False) <= 1:
        constant_features.append(col)

print(
    "Count:",
    len(constant_features)
)

for col in constant_features:
    print("-", col)

# ------------------------------------------------------------
# 5. Correlation
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("HIGHLY CORRELATED NUMERIC FEATURES")
print("=" * 70)

corr = (
    df[numeric_columns]
    .corr()
    .abs()
)

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

pairs = sorted(
    pairs,
    key=lambda x: x[2],
    reverse=True
)

if pairs:

    for a, b, value in pairs:
        print(
            f"{a} <-> {b}: {value:.4f}"
        )

else:

    print(
        "No feature pairs above 0.90 correlation."
    )

# ------------------------------------------------------------
# 6. Profile outcomes
# ------------------------------------------------------------

if "credit_outcome" in df.columns:

    print("\n" + "=" * 70)
    print("ALTERNATIVE DATA PROFILE OUTCOME")
    print("=" * 70)

    print(
        df["credit_outcome"]
        .value_counts()
    )

# ------------------------------------------------------------
# 7. Risk buckets
# ------------------------------------------------------------

if "risk_bucket" in df.columns:

    print("\n" + "=" * 70)
    print("RISK BUCKET")
    print("=" * 70)

    print(
        df["risk_bucket"]
        .value_counts()
    )

# ------------------------------------------------------------
# 8. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("QUALITY CHECK COMPLETED")
print("=" * 70)