import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

# ============================================================
# CREDXAI - ALTERNATIVE DATA LOGISTIC REGRESSION
# ============================================================

INPUT = Path(
    "data/processed/alternative_model_dataset.csv"
)

MODEL_OUTPUT = Path(
    "models/alternative_logistic_regression.pkl"
)

print("=" * 80)
print("CREDXAI - ALTERNATIVE DATA LOGISTIC REGRESSION")
print("=" * 80)

# ------------------------------------------------------------
# 1. Load dataset
# ------------------------------------------------------------

print("\nLoading prepared dataset...")

df = pd.read_csv(INPUT)

print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 2. Separate features and target
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

print("\nFeature count:", X.shape[1])

print("\nTarget distribution:")
print(y.value_counts())

# ------------------------------------------------------------
# 3. Identify feature types
# ------------------------------------------------------------

categorical_features = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numeric_features = X.select_dtypes(
    include=["number"]
).columns.tolist()

print("\nCategorical features:")

for col in categorical_features:
    print("-", col)

print("\nNumeric features:")

for col in numeric_features:
    print("-", col)

# ------------------------------------------------------------
# 4. Numeric preprocessing
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
# 5. Categorical preprocessing
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
# 6. Combined preprocessing
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
# 7. Logistic Regression
# ------------------------------------------------------------

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    solver="liblinear",
    random_state=42
)

# ------------------------------------------------------------
# 8. Complete ML pipeline
# ------------------------------------------------------------

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            model
        )
    ]
)

# ------------------------------------------------------------
# 9. Cross-validation
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("STRATIFIED CROSS-VALIDATION")
print("=" * 80)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scoring = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc"
]

cv_results = cross_validate(
    pipeline,
    X,
    y,
    cv=cv,
    scoring=scoring,
    return_train_score=False
)

for metric in scoring:

    values = cv_results[
        "test_" + metric
    ]

    print(
        f"{metric.upper():<12}: "
        f"{values.mean():.4f} "
        f"+/- "
        f"{values.std():.4f}"
    )

# ------------------------------------------------------------
# 10. Train final model
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("TRAINING FINAL MODEL")
print("=" * 80)

pipeline.fit(
    X,
    y
)

print("Model training completed.")

# ------------------------------------------------------------
# 11. Training predictions
# ------------------------------------------------------------

predictions = pipeline.predict(X)

probabilities = pipeline.predict_proba(X)[:, 1]

print("\nTraining-set metrics")
print("(For reference only - not unbiased performance)")
print("-" * 50)

print(
    "Accuracy:",
    round(
        accuracy_score(
            y,
            predictions
        ),
        4
    )
)

print(
    "Precision:",
    round(
        precision_score(
            y,
            predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "Recall:",
    round(
        recall_score(
            y,
            predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "F1:",
    round(
        f1_score(
            y,
            predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "ROC-AUC:",
    round(
        roc_auc_score(
            y,
            probabilities
        ),
        4
    )
)

# ------------------------------------------------------------
# 12. Confusion matrix
# ------------------------------------------------------------

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y,
        predictions
    )
)

# ------------------------------------------------------------
# 13. Save model
# ------------------------------------------------------------

MODEL_OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    pipeline,
    MODEL_OUTPUT
)

print("\nModel saved to:")

print(MODEL_OUTPUT)

# ------------------------------------------------------------
# 14. Model information
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("MODEL INFORMATION")
print("=" * 80)

print(
    "Algorithm: Logistic Regression"
)

print(
    "Training applicants:",
    len(df)
)

print(
    "Good applicants:",
    int((y == 0).sum())
)

print(
    "Bad applicants:",
    int((y == 1).sum())
)

print(
    "Input features:",
    X.shape[1]
)

print(
    "Excluded leakage fields:"
)

print(
    "- default_probability"
)

print(
    "- risk_behavior_score"
)

print("\n" + "=" * 80)
print("ALTERNATIVE MODEL TRAINING COMPLETED")
print("=" * 80)