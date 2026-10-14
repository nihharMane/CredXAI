import pandas as pd
from pathlib import Path

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# ============================================================
# CREDXAI - THRESHOLD ANALYSIS
# ============================================================

INPUT = Path(
    "outputs/logistic_test_predictions.csv"
)

print("=" * 70)
print("CREDXAI - DECISION THRESHOLD ANALYSIS")
print("=" * 70)

df = pd.read_csv(INPUT)

y_true = df["ACTUAL_TARGET"]
probability = df["DEFAULT_PROBABILITY"]

# ------------------------------------------------------------
# Thresholds
# ------------------------------------------------------------

thresholds = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80
]

results = []

for threshold in thresholds:

    prediction = (
        probability >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        prediction
    ).ravel()

    precision = precision_score(
        y_true,
        prediction,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        prediction,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        prediction,
        zero_division=0
    )

    results.append(
        {
            "THRESHOLD": threshold,
            "TRUE_POSITIVE": tp,
            "FALSE_POSITIVE": fp,
            "TRUE_NEGATIVE": tn,
            "FALSE_NEGATIVE": fn,
            "PRECISION": precision,
            "RECALL": recall,
            "F1": f1
        }
    )

results_df = pd.DataFrame(results)

# ------------------------------------------------------------
# Print
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("THRESHOLD COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

# ------------------------------------------------------------
# Best F1 threshold
# ------------------------------------------------------------

best_f1 = results_df.loc[
    results_df["F1"].idxmax()
]

print("\n" + "=" * 70)
print("BEST F1 THRESHOLD")
print("=" * 70)

print(
    best_f1.to_string()
)

# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

OUTPUT = Path(
    "outputs/threshold_analysis.csv"
)

results_df.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved to:")
print(OUTPUT)

print("\nThreshold analysis completed.")
print("=" * 70)