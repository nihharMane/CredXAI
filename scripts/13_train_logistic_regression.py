import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix
)

# ============================================================
# CREDXAI - LOGISTIC REGRESSION
# ============================================================

INPUT = Path(
    "data/processed/model_dataset.csv"
)

MODEL_DIR = Path("models")
OUTPUT_DIR = Path("outputs")

print("=" * 70)
print("CREDXAI - LOGISTIC REGRESSION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

print("\nLoading model dataset...")

df = pd.read_csv(INPUT)

print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 2. Separate ID, features and target
# ------------------------------------------------------------

applicant_ids = df["SK_ID_CURR"]

X = df.drop(
    columns=["SK_ID_CURR", "TARGET"]
)

y = df["TARGET"]

print("\nFeature matrix:")
print(X.shape)

print("\nTarget:")
print(y.value_counts())

# ------------------------------------------------------------
# 3. Train / test split
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT")
print("=" * 70)

X_train, X_test, y_train, y_test, id_train, id_test = (
    train_test_split(
        X,
        y,
        applicant_ids,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
)

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

print("\nTraining target percentage:")
print(
    (y_train.value_counts(normalize=True) * 100).round(2)
)

print("\nTesting target percentage:")
print(
    (y_test.value_counts(normalize=True) * 100).round(2)
)

# ------------------------------------------------------------
# 4. Identify feature types
# ------------------------------------------------------------

numeric_features = X_train.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_features = X_train.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

print("\nNumeric features:", len(numeric_features))
print("Categorical features:", len(categorical_features))

# ------------------------------------------------------------
# 5. Numeric preprocessing
# ------------------------------------------------------------

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)

# ------------------------------------------------------------
# 6. Categorical preprocessing
# ------------------------------------------------------------

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

# ------------------------------------------------------------
# 7. Combined preprocessing
# ------------------------------------------------------------

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
# 8. Logistic Regression
# ------------------------------------------------------------

logistic_model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

# ------------------------------------------------------------
# 9. Complete pipeline
# ------------------------------------------------------------

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            logistic_model
        )
    ]
)

# ------------------------------------------------------------
# 10. Train
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAINING LOGISTIC REGRESSION")
print("=" * 70)

print("\nTraining started...")

model.fit(
    X_train,
    y_train
)

print("Training completed successfully.")

# ------------------------------------------------------------
# 11. Predictions
# ------------------------------------------------------------

print("\nGenerating predictions...")

y_probability = model.predict_proba(
    X_test
)[:, 1]

# Default threshold = 0.5 for initial evaluation
y_prediction = (
    y_probability >= 0.5
).astype(int)

# ------------------------------------------------------------
# 12. Evaluation
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)

pr_auc = average_precision_score(
    y_test,
    y_probability
)

print(
    f"\nROC-AUC: {roc_auc:.4f}"
)

print(
    f"PR-AUC:  {pr_auc:.4f}"
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_prediction
    )
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_prediction,
        digits=4
    )
)

# ------------------------------------------------------------
# 13. Save test predictions
# ------------------------------------------------------------

results = pd.DataFrame(
    {
        "SK_ID_CURR": id_test.values,
        "ACTUAL_TARGET": y_test.values,
        "DEFAULT_PROBABILITY": y_probability,
        "PREDICTED_TARGET": y_prediction
    }
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

results.to_csv(
    OUTPUT_DIR / "logistic_test_predictions.csv",
    index=False
)

# ------------------------------------------------------------
# 14. Save model
# ------------------------------------------------------------

import joblib

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_DIR / "logistic_regression.pkl"
)

# ------------------------------------------------------------
# 15. Final message
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(
    "Model:",
    "models/logistic_regression.pkl"
)

print(
    "Test predictions:",
    "outputs/logistic_test_predictions.csv"
)

print("\nIMPORTANT:")
print("The test set was NOT used during training.")

print("\nLogistic Regression training completed.")
print("=" * 70)