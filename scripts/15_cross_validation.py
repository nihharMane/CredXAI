import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

from pathlib import Path

# ============================================================
# CREDXAI - CROSS VALIDATION
# ============================================================

INPUT = Path(
    "data/processed/model_dataset.csv"
)

print("=" * 70)
print("CREDXAI - LOGISTIC REGRESSION CROSS VALIDATION")
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
# 2. Feature types
# ------------------------------------------------------------

numeric_features = X.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_features = X.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

# ------------------------------------------------------------
# 3. Preprocessing
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
# 4. Logistic Regression
# ------------------------------------------------------------

classifier = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            classifier
        )
    ]
)

# ------------------------------------------------------------
# 5. Stratified 5-fold CV
# ------------------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

print("\nRunning 5-fold cross-validation...")

scores = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=[
        "roc_auc",
        "average_precision",
        "recall",
        "precision",
        "f1"
    ],
    n_jobs=-1
)

# ------------------------------------------------------------
# 6. Results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CROSS-VALIDATION RESULTS")
print("=" * 70)

metrics = {
    "ROC-AUC": "test_roc_auc",
    "PR-AUC": "test_average_precision",
    "Recall": "test_recall",
    "Precision": "test_precision",
    "F1": "test_f1"
}

for name, column in metrics.items():

    values = scores[column]

    print(
        f"{name:<12}: "
        f"{values.mean():.4f} "
        f"+/- {values.std():.4f}"
    )

    print(
        "  Folds:",
        [round(v, 4) for v in values]
    )

# ------------------------------------------------------------
# 7. Final
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("CROSS-VALIDATION COMPLETED")
print("=" * 70)

print(
    """
Interpretation:

Low standard deviation between folds
means the model is relatively stable.

A large difference between folds
means performance varies significantly
depending on the training data.
"""
)

print("=" * 70)