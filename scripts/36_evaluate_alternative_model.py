import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score
)
from sklearn.inspection import permutation_importance


# ============================================================
# CREDXAI - ALTERNATIVE MODEL EVALUATION
# ============================================================

INPUT = Path(
    "data/processed/alternative_model_dataset.csv"
)

MODEL_INPUT = Path(
    "models/alternative_logistic_regression.pkl"
)

OUTPUT = Path(
    "outputs/alternative_model_evaluation.txt"
)


print("=" * 80)
print("CREDXAI - ALTERNATIVE MODEL EVALUATION")
print("=" * 80)


# ------------------------------------------------------------
# 1. Load dataset
# ------------------------------------------------------------

print("\nLoading dataset...")

df = pd.read_csv(INPUT)

print("Rows:", len(df))
print("Columns:", len(df.columns))


# ------------------------------------------------------------
# 2. Prepare X and y
# ------------------------------------------------------------

DROP_COLUMNS = [
    "user_id",
    "credit_outcome",
    "TARGET"
]

X = df.drop(
    columns=DROP_COLUMNS
)

y = df["TARGET"]


print("\nFeatures:", X.shape[1])

print("\nTarget distribution:")
print(y.value_counts())


# ------------------------------------------------------------
# 3. Load model
# ------------------------------------------------------------

print("\nLoading trained model...")

model = joblib.load(MODEL_INPUT)

print("Model loaded successfully.")


# ------------------------------------------------------------
# 4. Cross-validation predictions
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("CROSS-VALIDATION PREDICTIONS")
print("=" * 80)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

predictions = cross_val_predict(
    model,
    X,
    y,
    cv=cv,
    method="predict"
)

probabilities = cross_val_predict(
    model,
    X,
    y,
    cv=cv,
    method="predict_proba"
)[:, 1]


print("\nCross-validation predictions:")

result = pd.DataFrame({
    "user_id": df["user_id"],
    "actual": y,
    "predicted": predictions,
    "bad_probability": probabilities
})

print(
    result.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 5. Confusion matrix
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("CONFUSION MATRIX")
print("=" * 80)

cm = confusion_matrix(
    y,
    predictions
)

print(cm)


# ------------------------------------------------------------
# 6. Classification report
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("CLASSIFICATION REPORT")
print("=" * 80)

report = classification_report(
    y,
    predictions,
    target_names=[
        "GOOD",
        "BAD"
    ],
    zero_division=0
)

print(report)


# ------------------------------------------------------------
# 7. ROC-AUC
# ------------------------------------------------------------

auc = roc_auc_score(
    y,
    probabilities
)

print(
    "Cross-validation ROC-AUC:",
    round(auc, 4)
)


# ------------------------------------------------------------
# 8. Feature permutation importance
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("PERMUTATION FEATURE IMPORTANCE")
print("=" * 80)

print(
    "\nCalculating feature importance..."
)

importance = permutation_importance(
    model,
    X,
    y,
    scoring="roc_auc",
    n_repeats=10,
    random_state=42
)

importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance_mean": importance.importances_mean,
    "importance_std": importance.importances_std
})

importance_df = importance_df.sort_values(
    "importance_mean",
    ascending=False
)

print(
    importance_df.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 9. Class-wise feature comparison
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("GOOD VS BAD FEATURE COMPARISON")
print("=" * 80)

numeric_features = X.select_dtypes(
    include=["number"]
).columns

comparison = []

for feature in numeric_features:

    good_mean = df.loc[
        df["TARGET"] == 0,
        feature
    ].mean()

    bad_mean = df.loc[
        df["TARGET"] == 1,
        feature
    ].mean()

    comparison.append({
        "feature": feature,
        "good_mean": good_mean,
        "bad_mean": bad_mean,
        "absolute_difference": abs(
            bad_mean - good_mean
        )
    })

comparison_df = pd.DataFrame(
    comparison
).sort_values(
    "absolute_difference",
    ascending=False
)

print(
    comparison_df.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 10. Check suspicious correlations
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TARGET CORRELATION CHECK")
print("=" * 80)

correlation_df = df[
    numeric_features.tolist() + ["TARGET"]
].corr()["TARGET"].drop(
    "TARGET"
).abs().sort_values(
    ascending=False
)

print(correlation_df.to_string())


# ------------------------------------------------------------
# 11. Check exact target separation
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TARGET SEPARATION CHECK")
print("=" * 80)

for feature in numeric_features:

    good = df.loc[
        df["TARGET"] == 0,
        feature
    ]

    bad = df.loc[
        df["TARGET"] == 1,
        feature
    ]

    good_max = good.max()
    bad_min = bad.min()

    good_min = good.min()
    bad_max = bad.max()

    if bad_min > good_max:

        print(
            f"\n{feature}:"
        )

        print(
            "BAD minimum > GOOD maximum"
        )

        print(
            "GOOD max:",
            good_max
        )

        print(
            "BAD min:",
            bad_min
        )

    elif good_min > bad_max:

        print(
            f"\n{feature}:"
        )

        print(
            "GOOD minimum > BAD maximum"
        )

        print(
            "GOOD min:",
            good_min
        )

        print(
            "BAD max:",
            bad_max
        )


# ------------------------------------------------------------
# 12. Save evaluation report
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "CREDXAI - ALTERNATIVE MODEL EVALUATION\n"
    )

    file.write(
        "=" * 80 + "\n\n"
    )

    file.write(
        f"Rows: {len(df)}\n"
    )

    file.write(
        f"Features: {X.shape[1]}\n"
    )

    file.write(
        f"ROC-AUC: {auc:.4f}\n\n"
    )

    file.write(
        "CLASSIFICATION REPORT\n"
    )

    file.write(
        report
    )

    file.write(
        "\n\nPERMUTATION IMPORTANCE\n"
    )

    file.write(
        importance_df.to_string(
            index=False
        )
    )

    file.write(
        "\n\nFEATURE COMPARISON\n"
    )

    file.write(
        comparison_df.to_string(
            index=False
        )
    )

print("\nEvaluation report saved to:")

print(OUTPUT)


print("\n" + "=" * 80)
print("ALTERNATIVE MODEL EVALUATION COMPLETED")
print("=" * 80)