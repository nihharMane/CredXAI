import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - PREPARE MODEL DATA
# ============================================================

INPUT = Path(
    "data/processed/final_home_credit_dataset.csv"
)

OUTPUT = Path(
    "data/processed/model_dataset.csv"
)

print("=" * 70)
print("CREDXAI - MODEL DATA PREPARATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load final dataset
# ------------------------------------------------------------

print("\nLoading final dataset...")

df = pd.read_csv(INPUT)

print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# 2. Remove ID from model features
# ------------------------------------------------------------

if "SK_ID_CURR" not in df.columns:
    raise ValueError("SK_ID_CURR not found.")

# Keep ID for applicant identification
applicant_id = df["SK_ID_CURR"]

df = df.drop(
    columns=["SK_ID_CURR"]
)

# ------------------------------------------------------------
# 3. Remove potentially ambiguous default-derived features
# ------------------------------------------------------------

remove_columns = [
    "DPD_DEFAULT_COUNT",
    "DPD_DEFAULT_RATIO",
    "POS_DPD_DEFAULT_COUNT",
    "POS_DPD_DEFAULT_RATIO"
]

existing_remove_columns = [
    col for col in remove_columns
    if col in df.columns
]

df = df.drop(
    columns=existing_remove_columns
)

print("\nRemoved columns:")

for col in ["SK_ID_CURR"] + existing_remove_columns:
    print("-", col)

# ------------------------------------------------------------
# 4. Check TARGET
# ------------------------------------------------------------

if "TARGET" not in df.columns:
    raise ValueError("TARGET column not found.")

print("\nTARGET distribution:")

print(
    df["TARGET"].value_counts()
)

print("\nTARGET percentage:")

print(
    (
        df["TARGET"]
        .value_counts(normalize=True)
        * 100
    ).round(2)
)

# ------------------------------------------------------------
# 5. Separate target
# ------------------------------------------------------------

y = df["TARGET"]

X = df.drop(
    columns=["TARGET"]
)

# ------------------------------------------------------------
# 6. Identify column types
# ------------------------------------------------------------

numeric_columns = X.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_columns = X.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

print("\n" + "=" * 70)
print("FEATURE TYPES")
print("=" * 70)

print(
    "Numeric features:",
    len(numeric_columns)
)

print(
    "Categorical features:",
    len(categorical_columns)
)

print("\nCategorical columns:")

for col in categorical_columns:
    print("-", col)

# ------------------------------------------------------------
# 7. Check infinite values
# ------------------------------------------------------------

numeric_X = X[numeric_columns]

infinite_values = (
    np.isinf(numeric_X)
    .sum()
    .sum()
)

print("\nInfinite values:", infinite_values)

# ------------------------------------------------------------
# 8. Save modelling dataset
# ------------------------------------------------------------

# Add applicant ID back only for identification.
# It will NOT be used as a model feature.

model_df = X.copy()

model_df.insert(
    0,
    "SK_ID_CURR",
    applicant_id
)

model_df["TARGET"] = y

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

model_df.to_csv(
    OUTPUT,
    index=False
)

print("\n" + "=" * 70)
print("MODEL DATASET CREATED")
print("=" * 70)

print("Rows:", len(model_df))
print("Columns:", len(model_df.columns))

print("\nSaved to:")
print(OUTPUT)

print("\nIMPORTANT:")
print("SK_ID_CURR is retained only for applicant identification.")
print("It will NOT be used as a model feature.")

print("\nModel-data preparation completed.")
print("=" * 70)