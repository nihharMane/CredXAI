import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

# ============================================================
# CREDXAI - PROBABILITY CALIBRATION CHECK
# ============================================================

INPUT = Path(
    "outputs/logistic_test_predictions.csv"
)

OUTPUT = Path(
    "outputs/probability_calibration.csv"
)

print("=" * 70)
print("CREDXAI - PROBABILITY CALIBRATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load predictions
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

y_true = df["ACTUAL_TARGET"]
probability = df["DEFAULT_PROBABILITY"]

# ------------------------------------------------------------
# 2. Brier score
# ------------------------------------------------------------

brier = brier_score_loss(
    y_true,
    probability
)

print("\nBrier Score:")
print(f"{brier:.6f}")

# ------------------------------------------------------------
# 3. Calibration bins
# ------------------------------------------------------------

fraction_positive, mean_probability = calibration_curve(
    y_true,
    probability,
    n_bins=10,
    strategy="quantile"
)

# ------------------------------------------------------------
# 4. Create calibration table
# ------------------------------------------------------------

calibration_df = pd.DataFrame(
    {
        "MEAN_PREDICTED_PROBABILITY":
            mean_probability,
        "ACTUAL_DEFAULT_RATE":
            fraction_positive
    }
)

calibration_df[
    "ABSOLUTE_DIFFERENCE"
] = (
    calibration_df[
        "MEAN_PREDICTED_PROBABILITY"
    ]
    -
    calibration_df[
        "ACTUAL_DEFAULT_RATE"
    ]
).abs()

print("\n" + "=" * 70)
print("CALIBRATION TABLE")
print("=" * 70)

print(
    calibration_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

# ------------------------------------------------------------
# 5. Save
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

calibration_df.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved to:")
print(OUTPUT)

print("\nCalibration check completed.")
print("=" * 70)