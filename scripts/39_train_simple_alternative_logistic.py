import joblib
import pandas as pd

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_validate


# ============================================================
# CREDXAI - SIMPLE ALTERNATIVE LOGISTIC REGRESSION
# ============================================================

INPUT = Path(
    "data/processed/simple_alternative_model_dataset.csv"
)

OUTPUT = Path(
    "models/simple_alternative_logistic_regression.pkl"
)

print("=" * 70)
print("CREDXAI - SIMPLE ALTERNATIVE LOGISTIC REGRESSION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

print("\nRows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 2. Features and target
# ------------------------------------------------------------

features = [
    "age_range",
    "account_tenure_days",
    "avg_monthly_income",
    "avg_monthly_spend",
    "avg_balance",
    "overdraft_frequency",
    "bill_payment_consistency",
    "cashflow_stability_score"
]

X = df[features]

y = df["TARGET"]

print("\nFeature count:", len(features))

print("\nTarget distribution:")

print(
    y.value_counts()
)

# ------------------------------------------------------------
# 3. Feature types
# ------------------------------------------------------------

categorical_features = [
    "age_range"
]

numeric_features = [
    "account_tenure_days",
    "avg_monthly_income",
    "avg_monthly_spend",
    "avg_balance",
    "overdraft_frequency",
    "bill_payment_consistency",
    "cashflow_stability_score"
]

# ------------------------------------------------------------
# 4. Preprocessing
# ------------------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[

        (
            "numeric",
            StandardScaler(),
            numeric_features
        ),

        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ]
)

# ------------------------------------------------------------
# 5. Logistic Regression
# ------------------------------------------------------------

model = Pipeline(
    steps=[

        (
            "preprocessing",
            preprocessor
        ),

        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42
            )
        )
    ]
)

# ------------------------------------------------------------
# 6. Cross-validation
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STRATIFIED CROSS-VALIDATION")
print("=" * 70)

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

results = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=scoring
)

print(
    f"ACCURACY  : "
    f"{results['test_accuracy'].mean():.4f}"
)

print(
    f"PRECISION : "
    f"{results['test_precision'].mean():.4f}"
)

print(
    f"RECALL    : "
    f"{results['test_recall'].mean():.4f}"
)

print(
    f"F1        : "
    f"{results['test_f1'].mean():.4f}"
)

print(
    f"ROC_AUC   : "
    f"{results['test_roc_auc'].mean():.4f}"
)

# ------------------------------------------------------------
# 7. Train final model
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAINING FINAL MODEL")
print("=" * 70)

model.fit(
    X,
    y
)

print("Training completed.")

# ------------------------------------------------------------
# 8. Save model
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    OUTPUT
)

print("\nModel saved to:")

print(OUTPUT)

# ------------------------------------------------------------
# 9. Model information
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL INFORMATION")
print("=" * 70)

print("Algorithm: Logistic Regression")
print("Training applicants:", len(df))
print("Input features:", len(features))

print("\nFeatures:")

for feature in features:
    print("-", feature)

print("\n" + "=" * 70)
print("SIMPLE ALTERNATIVE MODEL TRAINING COMPLETED")
print("=" * 70)