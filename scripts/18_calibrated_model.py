import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss
)

# ============================================================
# CREDXAI - CALIBRATED LOGISTIC REGRESSION
# ============================================================

INPUT = Path(
    "data/processed/model_dataset.csv"
)

MODEL_DIR = Path("models")
OUTPUT_DIR = Path("outputs")

print("=" * 70)
print("CREDXAI - CALIBRATED LOGISTIC REGRESSION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

X = df.drop(
    columns=["SK_ID_CURR", "TARGET"]
)

y = df["TARGET"]

# ------------------------------------------------------------
# 2. 60 / 20 / 20 split
# ------------------------------------------------------------

print("\nCreating train / validation / test split...")

X_temp, X_test, y_temp, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

X_train, X_validation, y_train, y_validation = train_test_split(
    X_temp,
    y_temp,
    test_size=0.25,
    random_state=42,
    stratify=y_temp
)

print("\nDataset split:")
print("Training:", len(X_train))
print("Validation:", len(X_validation))
print("Final test:", len(X_test))

# ------------------------------------------------------------
# 3. Feature types
# ------------------------------------------------------------

numeric_features = X_train.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_features = X_train.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

# ------------------------------------------------------------
# 4. Preprocessing
# ------------------------------------------------------------

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(handle_unknown="ignore")
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)

# ------------------------------------------------------------
# 5. Base Logistic Regression
# ------------------------------------------------------------

base_logistic = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

base_pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            base_logistic
        )
    ]
)

# ------------------------------------------------------------
# 6. Calibrated classifier
# ------------------------------------------------------------

print("\nTraining calibrated Logistic Regression...")

calibrated_model = CalibratedClassifierCV(
    estimator=base_pipeline,
    method="sigmoid",
    cv=5
)

calibrated_model.fit(
    X_train,
    y_train
)

print("Training completed.")

# ------------------------------------------------------------
# 7. Validation predictions
# ------------------------------------------------------------

validation_probability = calibrated_model.predict_proba(
    X_validation
)[:, 1]

# ------------------------------------------------------------
# 8. Validation metrics
# ------------------------------------------------------------

validation_auc = roc_auc_score(
    y_validation,
    validation_probability
)

validation_pr_auc = average_precision_score(
    y_validation,
    validation_probability
)

validation_brier = brier_score_loss(
    y_validation,
    validation_probability
)

print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

print(
    f"ROC-AUC: {validation_auc:.4f}"
)

print(
    f"PR-AUC:  {validation_pr_auc:.4f}"
)

print(
    f"Brier:   {validation_brier:.6f}"
)

# ------------------------------------------------------------
# 9. Final test predictions
# ------------------------------------------------------------

print("\nEvaluating on final unseen test set...")

test_probability = calibrated_model.predict_proba(
    X_test
)[:, 1]

test_auc = roc_auc_score(
    y_test,
    test_probability
)

test_pr_auc = average_precision_score(
    y_test,
    test_probability
)

test_brier = brier_score_loss(
    y_test,
    test_probability
)

print("\n" + "=" * 70)
print("FINAL UNSEEN TEST RESULTS")
print("=" * 70)

print(
    f"ROC-AUC: {test_auc:.4f}"
)

print(
    f"PR-AUC:  {test_pr_auc:.4f}"
)

print(
    f"Brier:   {test_brier:.6f}"
)

# ------------------------------------------------------------
# 10. Save test predictions
# ------------------------------------------------------------

test_results = pd.DataFrame(
    {
        "ACTUAL_TARGET": y_test.values,
        "CALIBRATED_DEFAULT_PROBABILITY":
            test_probability
    }
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

test_results.to_csv(
    OUTPUT_DIR / "calibrated_test_predictions.csv",
    index=False
)

# ------------------------------------------------------------
# 11. Save model
# ------------------------------------------------------------

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    calibrated_model,
    MODEL_DIR / "calibrated_logistic_regression.pkl"
)

print("\n" + "=" * 70)
print("CALIBRATED MODEL SAVED")
print("=" * 70)

print(
    "models/calibrated_logistic_regression.pkl"
)

print(
    "outputs/calibrated_test_predictions.csv"
)

print("\nCompleted.")
print("=" * 70)