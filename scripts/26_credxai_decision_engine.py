import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - DECISION ENGINE
# ============================================================

INPUT = Path(
    "data/processed/alternative_scored_profiles.csv"
)

OUTPUT = Path(
    "data/processed/alternative_decision_profiles.csv"
)

print("=" * 70)
print("CREDXAI - DECISION ENGINE")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load alternative profiles
# ------------------------------------------------------------

print("\nLoading alternative scored profiles...")

df = pd.read_csv(INPUT)

print("Clients:", len(df))

# ------------------------------------------------------------
# 2. Create decision contribution
# ------------------------------------------------------------

# The alternative score is a supporting signal.
#
# It is NOT a default probability.
#
# Higher financial-health score = better profile.

def alternative_contribution(score):

    if score >= 70:
        return "SUPPORTIVE"

    elif score >= 45:
        return "NEUTRAL"

    else:
        return "CAUTION"


df["ALTERNATIVE_SIGNAL"] = (
    df["ALTERNATIVE_FINANCIAL_HEALTH_SCORE"]
    .apply(alternative_contribution)
)

# ------------------------------------------------------------
# 3. Alternative risk level
# ------------------------------------------------------------

def risk_level(score):

    if score >= 70:
        return "LOW"

    elif score >= 45:
        return "MEDIUM"

    else:
        return "HIGH"


df["ALTERNATIVE_RISK_LEVEL"] = (
    df["ALTERNATIVE_FINANCIAL_HEALTH_SCORE"]
    .apply(risk_level)
)

# ------------------------------------------------------------
# 4. Generate explanation
# ------------------------------------------------------------

def generate_explanation(row):

    reasons = []

    # Positive signals

    if row["CREDIT_SCORE"] >= 750:
        reasons.append(
            "strong credit score"
        )

    elif row["CREDIT_SCORE"] < 600:
        reasons.append(
            "low credit score"
        )

    if row["DEBT_TO_INCOME_RATIO"] <= 0.20:
        reasons.append(
            "low debt-to-income ratio"
        )

    elif row["DEBT_TO_INCOME_RATIO"] > 0.40:
        reasons.append(
            "high debt-to-income ratio"
        )

    if row["HIGH_VALUE_TRANSACTION_RATIO"] > 0.50:
        reasons.append(
            "high concentration of high-value transactions"
        )

    if row["TRANSACTION_HISTORY_DAYS"] >= 365:
        reasons.append(
            "substantial transaction history"
        )

    if row["DIGITAL_TRANSACTION_RATIO"] >= 0.75:
        reasons.append(
            "consistent digital transaction activity"
        )

    if row["HIGH_SPENDING_VOLATILITY_FLAG"] == 1:
        reasons.append(
            "high spending volatility"
        )

    # No special reason

    if not reasons:
        reasons.append(
            "no major behavioral warning signal"
        )

    return "; ".join(reasons)


df["ALTERNATIVE_EXPLANATION"] = (
    df.apply(
        generate_explanation,
        axis=1
    )
)

# ------------------------------------------------------------
# 5. Overall behavioral interpretation
# ------------------------------------------------------------

def behavioral_interpretation(row):

    score = row[
        "ALTERNATIVE_FINANCIAL_HEALTH_SCORE"
    ]

    warnings = row[
        "BEHAVIORAL_WARNING_COUNT"
    ]

    if score >= 70 and warnings == 0:

        return "FINANCIALLY_STABLE"

    elif score >= 45 and warnings <= 1:

        return "MODERATE_BEHAVIORAL_RISK"

    else:

        return "BEHAVIORAL_CAUTION"


df["BEHAVIORAL_INTERPRETATION"] = (
    df.apply(
        behavioral_interpretation,
        axis=1
    )
)

# ------------------------------------------------------------
# 6. Save
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
# 7. Display results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ALTERNATIVE DECISION RESULTS")
print("=" * 70)

print(
    "\nSignal distribution:"
)

print(
    df[
        "ALTERNATIVE_SIGNAL"
    ].value_counts()
)

print(
    "\nRisk-level distribution:"
)

print(
    df[
        "ALTERNATIVE_RISK_LEVEL"
    ].value_counts()
)

print(
    "\nBehavioral interpretation:"
)

print(
    df[
        "BEHAVIORAL_INTERPRETATION"
    ].value_counts()
)

print(
    "\nExample profiles:"
)

print(
    df[
        [
            "client_id",
            "CREDIT_SCORE",
            "DEBT_TO_INCOME_RATIO",
            "TRANSACTION_COUNT",
            "DIGITAL_TRANSACTION_RATIO",
            "HIGH_VALUE_TRANSACTION_RATIO",
            "ALTERNATIVE_FINANCIAL_HEALTH_SCORE",
            "ALTERNATIVE_RISK_LEVEL",
            "ALTERNATIVE_SIGNAL",
            "BEHAVIORAL_INTERPRETATION",
            "ALTERNATIVE_EXPLANATION"
        ]
    ]
    .head(15)
    .to_string(index=False)
)

print("\nSaved to:")
print(OUTPUT)

print("\n" + "=" * 70)
print("DECISION ENGINE COMPLETED")
print("=" * 70)