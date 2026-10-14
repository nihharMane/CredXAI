import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - ALTERNATIVE FINANCIAL HEALTH SCORE
# ============================================================

INPUT = Path(
    "data/processed/indian_alternative_features.csv"
)

OUTPUT = Path(
    "data/processed/alternative_scored_profiles.csv"
)

print("=" * 70)
print("CREDXAI - ALTERNATIVE FINANCIAL HEALTH SCORE")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

print("\nLoading alternative features...")

df = pd.read_csv(INPUT)

print("Clients:", len(df))
print("Features:", len(df.columns))

# ------------------------------------------------------------
# 2. Helper function
# ------------------------------------------------------------

def min_max_score(series, higher_is_better=True):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        score = pd.Series(
            50.0,
            index=series.index
        )

    else:

        score = (
            (series - minimum)
            / (maximum - minimum)
            * 100
        )

    if not higher_is_better:
        score = 100 - score

    return score


# ------------------------------------------------------------
# 3. Credit score component
# ------------------------------------------------------------

# Higher credit score = better financial health

df["CREDIT_HEALTH_SCORE"] = min_max_score(
    df["CREDIT_SCORE"],
    higher_is_better=True
)

# ------------------------------------------------------------
# 4. Debt component
# ------------------------------------------------------------

# Lower debt-to-income = better

df["DEBT_HEALTH_SCORE"] = min_max_score(
    df["DEBT_TO_INCOME_RATIO"],
    higher_is_better=False
)

# ------------------------------------------------------------
# 5. Transaction history component
# ------------------------------------------------------------

# More transaction history = more behavioral information.
# We cap the effect so very long histories don't dominate.

history_capped = df[
    "TRANSACTION_HISTORY_DAYS"
].clip(
    upper=730
)

df["HISTORY_SCORE"] = (
    history_capped / 730 * 100
)

# ------------------------------------------------------------
# 6. Digital transaction component
# ------------------------------------------------------------

# Digital activity is treated as a behavioral signal,
# NOT as inherently good or bad.

df["DIGITAL_ACTIVITY_SCORE"] = (
    df["DIGITAL_TRANSACTION_RATIO"] * 100
)

# ------------------------------------------------------------
# 7. Spending stability component
# ------------------------------------------------------------

# Lower spending volatility relative to spending level
# indicates more stable spending.

spending_ratio = np.where(
    df["AVG_MONTHLY_SPENDING"] > 0,
    df["STD_MONTHLY_SPENDING"]
    / df["AVG_MONTHLY_SPENDING"],
    0
)

# Prevent extreme values from dominating.

spending_ratio = np.clip(
    spending_ratio,
    0,
    2
)

df["SPENDING_STABILITY_SCORE"] = (
    100 - (spending_ratio / 2 * 100)
)

# ------------------------------------------------------------
# 8. High-value spending component
# ------------------------------------------------------------

# Lower concentration of high-value transactions
# is treated as lower behavioral risk.

df["SPENDING_BEHAVIOR_SCORE"] = (
    100
    - (
        df["HIGH_VALUE_TRANSACTION_RATIO"]
        * 100
    )
)

# ------------------------------------------------------------
# 9. Transaction consistency component
# ------------------------------------------------------------

# More transactions provide more behavioral evidence.
# Cap at 10 transactions.

transaction_capped = df[
    "TRANSACTION_COUNT"
].clip(
    upper=10
)

df["TRANSACTION_ACTIVITY_SCORE"] = (
    transaction_capped / 10 * 100
)

# ------------------------------------------------------------
# 10. Overall Alternative Financial Health Score
# ------------------------------------------------------------

df["ALTERNATIVE_FINANCIAL_HEALTH_SCORE"] = (

    df["CREDIT_HEALTH_SCORE"] * 0.30

    + df["DEBT_HEALTH_SCORE"] * 0.25

    + df["HISTORY_SCORE"] * 0.10

    + df["SPENDING_STABILITY_SCORE"] * 0.15

    + df["SPENDING_BEHAVIOR_SCORE"] * 0.10

    + df["TRANSACTION_ACTIVITY_SCORE"] * 0.10
)

# Ensure score remains between 0 and 100.

df["ALTERNATIVE_FINANCIAL_HEALTH_SCORE"] = (
    df["ALTERNATIVE_FINANCIAL_HEALTH_SCORE"]
    .clip(0, 100)
)

# ------------------------------------------------------------
# 11. Risk category
# ------------------------------------------------------------

def classify_score(score):

    if score >= 70:
        return "LOW_RISK"

    elif score >= 45:
        return "MEDIUM_RISK"

    else:
        return "HIGH_RISK"


df["ALTERNATIVE_RISK_CATEGORY"] = (
    df["ALTERNATIVE_FINANCIAL_HEALTH_SCORE"]
    .apply(classify_score)
)

# ------------------------------------------------------------
# 12. Identify major behavioral concerns
# ------------------------------------------------------------

df["HIGH_DEBT_FLAG"] = (
    df["DEBT_TO_INCOME_RATIO"] > 0.40
).astype(int)

df["HIGH_SPENDING_VOLATILITY_FLAG"] = (
    spending_ratio > 1.0
).astype(int)

df["HIGH_VALUE_SPENDING_FLAG"] = (
    df["HIGH_VALUE_TRANSACTION_RATIO"] > 0.50
).astype(int)

df["LOW_CREDIT_SCORE_FLAG"] = (
    df["CREDIT_SCORE"] < 600
).astype(int)

# ------------------------------------------------------------
# 13. Count behavioral warning signals
# ------------------------------------------------------------

df["BEHAVIORAL_WARNING_COUNT"] = (
    df["HIGH_DEBT_FLAG"]
    + df["HIGH_SPENDING_VOLATILITY_FLAG"]
    + df["HIGH_VALUE_SPENDING_FLAG"]
    + df["LOW_CREDIT_SCORE_FLAG"]
)

# ------------------------------------------------------------
# 14. Save
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT,
    index=False
)

# ------------------------------------------------------------
# 15. Results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ALTERNATIVE SCORE CREATED")
print("=" * 70)

print(
    "\nScore statistics:"
)

print(
    df[
        "ALTERNATIVE_FINANCIAL_HEALTH_SCORE"
    ].describe()
)

print(
    "\nRisk category distribution:"
)

print(
    df[
        "ALTERNATIVE_RISK_CATEGORY"
    ].value_counts()
)

print(
    "\nWarning signal distribution:"
)

print(
    df[
        "BEHAVIORAL_WARNING_COUNT"
    ].value_counts()
    .sort_index()
)

print(
    "\nLowest 10 scores:"
)

print(
    df[
        [
            "client_id",
            "CREDIT_SCORE",
            "DEBT_TO_INCOME_RATIO",
            "HIGH_VALUE_TRANSACTION_RATIO",
            "ALTERNATIVE_FINANCIAL_HEALTH_SCORE",
            "ALTERNATIVE_RISK_CATEGORY"
        ]
    ]
    .sort_values(
        "ALTERNATIVE_FINANCIAL_HEALTH_SCORE"
    )
    .head(10)
    .to_string(index=False)
)

print(
    "\nHighest 10 scores:"
)

print(
    df[
        [
            "client_id",
            "CREDIT_SCORE",
            "DEBT_TO_INCOME_RATIO",
            "HIGH_VALUE_TRANSACTION_RATIO",
            "ALTERNATIVE_FINANCIAL_HEALTH_SCORE",
            "ALTERNATIVE_RISK_CATEGORY"
        ]
    ]
    .sort_values(
        "ALTERNATIVE_FINANCIAL_HEALTH_SCORE",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT)

print("\n" + "=" * 70)
print("ALTERNATIVE SCORING COMPLETED")
print("=" * 70)
