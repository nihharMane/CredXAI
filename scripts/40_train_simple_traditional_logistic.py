import pandas as pd
import joblib

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

# ============================================================
# CREDXAI - SIMPLE TRADITIONAL LOGISTIC REGRESSION
# ============================================================

print("=" * 70)
print("CREDXAI - SIMPLE TRADITIONAL LOGISTIC REGRESSION")
print("=" * 70)

# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

INPUT = Path(
    "data/processed/final_home_credit_dataset.csv"
)

OUTPUT = Path(
    "models/simple_traditional_logistic_regression.pkl"
)

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

print("\nLoading dataset...")

df = pd.read_csv(INPUT)

print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 12 USER INPUT FEATURES
# ------------------------------------------------------------

FEATURES = [
    "AGE_YEARS",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",
    "NAME_INCOME_TYPE",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "FLAG_OWN_CAR",
    "FLAG_OWN_REALTY",
    "NAME_EDUCATION_TYPE",
    "NAME_HOUSING_TYPE",
]

TARGET = "TARGET"

# ------------------------------------------------------------
# CHECK FEATURES
# ------------------------------------------------------------

print("\nChecking required columns...")

missing = [
    col for col in FEATURES + [TARGET]
    if col not in df.columns
]

if missing:
    print("\nERROR - Missing columns:")
    for col in missing:
        print("-", col)

    raise ValueError(
        "Required columns are missing from the dataset."
    )

print("All required columns found.")

# ------------------------------------------------------------
# SELECT DATA
# ------------------------------------------------------------

data = df[FEATURES + [TARGET]].copy()

# Remove rows without target
data = data.dropna(subset=[TARGET])

X = data[FEATURES]
y = data[TARGET].astype(int)

print("\nRows used:", len(data))

print("\nTarget distribution:")
print(y.value_counts())

# ------------------------------------------------------------
# FEATURE TYPES
# ------------------------------------------------------------

NUMERIC_FEATURES = [
    "AGE_YEARS",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
]

CATEGORICAL_FEATURES = [
    "NAME_INCOME_TYPE",
    "FLAG_OWN_CAR",
    "FLAG_OWN_REALTY",
    "NAME_EDUCATION_TYPE",
    "NAME_HOUSING_TYPE",
]

# ------------------------------------------------------------
# PREPROCESSING
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
        ),
    ]
)

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
        ),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            NUMERIC_FEATURES,
        ),
        (
            "categorical",
            categorical_pipeline,
            CATEGORICAL_FEATURES,
        ),
    ]
)

# ------------------------------------------------------------
# LOGISTIC REGRESSION
# ------------------------------------------------------------

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42,
)

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            model
        ),
    ]
)

# ------------------------------------------------------------
# STRATIFIED CROSS VALIDATION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STRATIFIED CROSS-VALIDATION")
print("=" * 70)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

probabilities = cross_val_predict(
    pipeline,
    X,
    y,
    cv=cv,
    method="predict_proba",
)[:, 1]

predictions = (
    probabilities >= 0.5
).astype(int)

accuracy = accuracy_score(
    y,
    predictions
)

precision = precision_score(
    y,
    predictions,
    zero_division=0
)

recall = recall_score(
    y,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y,
    predictions,
    zero_division=0
)

roc_auc = roc_auc_score(
    y,
    probabilities
)

print(
    f"ACCURACY  : {accuracy:.4f}"
)

print(
    f"PRECISION : {precision:.4f}"
)

print(
    f"RECALL    : {recall:.4f}"
)

print(
    f"F1        : {f1:.4f}"
)

print(
    f"ROC_AUC   : {roc_auc:.4f}"
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y,
        predictions
    )
)

print("\nClassification Report:")

print(
    classification_report(
        y,
        predictions,
        zero_division=0
    )
)

# ------------------------------------------------------------
# TRAIN FINAL MODEL
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRAINING FINAL MODEL")
print("=" * 70)

pipeline.fit(
    X,
    y
)

print("Training completed.")

# ------------------------------------------------------------
# SAVE MODEL
# ------------------------------------------------------------

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    pipeline,
    OUTPUT
)

print("\nModel saved to:")

print(OUTPUT)

# ------------------------------------------------------------
# MODEL INFORMATION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("MODEL INFORMATION")
print("=" * 70)

print("Algorithm: Logistic Regression")

print(
    "Training applicants:",
    len(data)
)

print(
    "User input features:",
    len(FEATURES)
)

print("\nFeatures:")

for feature in FEATURES:
    print("-", feature)

print("\n" + "=" * 70)
print("SIMPLE TRADITIONAL MODEL TRAINING COMPLETED")
print("=" * 70)