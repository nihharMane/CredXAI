import pandas as pd
from pathlib import Path

# ============================================================
# CREDXAI - FINAL RISK BAND ANALYSIS
# ============================================================

INPUT = Path(
    "outputs/calibrated_test_predictions.csv"
)

OUTPUT = Path(
    "outputs/final_risk_band_analysis.csv"
)

print("=" * 70)
print("CREDXAI - FINAL RISK BAND ANALYSIS")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load predictions
# ------------------------------------------------------------

print("\nLoading calibrated test predictions...")

df = pd.read_csv(INPUT)

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

# ------------------------------------------------------------
# 2. Inspect probability column
# ------------------------------------------------------------

print("\nFirst 5 predictions:")

print(
    df.head().to_string(index=False)
)

# ------------------------------------------------------------
# 3. Probability column
# ------------------------------------------------------------

probability_column = "CALIBRATED_DEFAULT_PROBABILITY"

if probability_column not in df.columns:

    raise ValueError(
        f"Column '{probability_column}' not found."
    )

print(
    "\nUsing probability column:",
    probability_column
)

# ------------------------------------------------------------
# 4. Target column
# ------------------------------------------------------------

target_column = "ACTUAL_TARGET"

if target_column not in df.columns:

    raise ValueError(
        f"Column '{target_column}' not found."
    )

print(
    "Using target column:",
    target_column
)

# ------------------------------------------------------------
# 5. Create risk bands
# ------------------------------------------------------------

def assign_risk_band(probability):

    if probability < 0.10:

        return "LOW_RISK"

    elif probability < 0.30:

        return "MEDIUM_RISK"

    else:

        return "HIGH_RISK"


df["RISK_BAND"] = (
    df[probability_column]
    .apply(assign_risk_band)
)

# ------------------------------------------------------------
# 6. Calculate band statistics
# ------------------------------------------------------------

summary = (
    df.groupby("RISK_BAND")
    .agg(
        APPLICANT_COUNT=(
            target_column,
            "count"
        ),

        ACTUAL_DEFAULTS=(
            target_column,
            "sum"
        ),

        AVERAGE_PREDICTED_PROBABILITY=(
            probability_column,
            "mean"
        ),

        ACTUAL_DEFAULT_RATE=(
            target_column,
            "mean"
        )
    )
    .reset_index()
)

summary["PERCENT_OF_TEST_SET"] = (
    summary["APPLICANT_COUNT"]
    / len(df)
    * 100
)

summary["ACTUAL_DEFAULT_RATE"] = (
    summary["ACTUAL_DEFAULT_RATE"]
    * 100
)

# ------------------------------------------------------------
# 7. Sort risk bands
# ------------------------------------------------------------

order = {
    "LOW_RISK": 0,
    "MEDIUM_RISK": 1,
    "HIGH_RISK": 2
}

summary["ORDER"] = (
    summary["RISK_BAND"]
    .map(order)
)

summary = (
    summary
    .sort_values("ORDER")
    .drop(columns="ORDER")
)

# ------------------------------------------------------------
# 8. Display results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL RISK BAND RESULTS")
print("=" * 70)

print(
    summary.to_string(
        index=False
    )
)

# ------------------------------------------------------------
# 9. Probability statistics
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PREDICTED PROBABILITY DISTRIBUTION")
print("=" * 70)

print(
    df[probability_column].describe()
)

# ------------------------------------------------------------
# 10. Save
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

summary.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved to:")
print(OUTPUT)

print("\n" + "=" * 70)
print("FINAL RISK BAND ANALYSIS COMPLETED")
print("=" * 70)
