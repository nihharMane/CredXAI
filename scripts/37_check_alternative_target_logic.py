import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - CHECK ALTERNATIVE TARGET LOGIC
# ============================================================

INPUT = Path(
    "data/external/electric_sheep_india/credit_profiles.parquet"
)

print("=" * 80)
print("CREDXAI - CHECK ALTERNATIVE TARGET LOGIC")
print("=" * 80)

df = pd.read_parquet(INPUT)

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
for col in df.columns:
    print("-", col)

print("\n" + "=" * 80)
print("TARGET DISTRIBUTION")
print("=" * 80)

if "credit_outcome" in df.columns:
    print(
        df["credit_outcome"].value_counts(
            dropna=False
        )
    )

print("\n" + "=" * 80)
print("TARGET VS IMPORTANT BEHAVIORAL FEATURES")
print("=" * 80)

features = [
    "default_probability",
    "risk_behavior_score",
    "overdraft_frequency",
    "cashflow_stability_score",
    "avg_balance",
    "min_balance",
    "max_balance",
    "betting_ratio",
    "bill_payment_consistency",
    "account_tenure_days"
]

available = [
    col
    for col in features
    if col in df.columns
]

for col in available:

    print("\n" + "-" * 60)
    print(col)

    print(
        df.groupby(
            "credit_outcome"
        )[col]
        .agg(
            [
                "count",
                "mean",
                "min",
                "max"
            ]
        )
        .to_string()
    )

print("\n" + "=" * 80)
print("TARGET AND RISK VARIABLES")
print("=" * 80)

if {
    "credit_outcome",
    "default_probability",
    "risk_behavior_score"
}.issubset(df.columns):

    print(
        df[
            [
                "credit_outcome",
                "default_probability",
                "risk_behavior_score"
            ]
        ]
        .sort_values(
            "default_probability",
            ascending=False
        )
        .to_string(index=False)
    )

print("\n" + "=" * 80)
print("SAMPLE ROWS")
print("=" * 80)

print(
    df.head(10).to_string(
        index=False
    )
)

print("\n" + "=" * 80)
print("TARGET LOGIC CHECK COMPLETED")
print("=" * 80)