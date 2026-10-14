import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI - DATA QUALITY CHECK
# ============================================================

DATA_PATH = Path("data/raw/home_credit/application_train.csv")

print("=" * 70)
print("CREDXAI - DATA QUALITY CHECK")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load application data
# ------------------------------------------------------------

print("\nLoading application_train.csv...")

df = pd.read_csv(DATA_PATH)

print("Loaded successfully.")

# ------------------------------------------------------------
# 2. Dataset size
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("1. DATASET SIZE")
print("=" * 70)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# ------------------------------------------------------------
# 3. Target
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("2. TARGET DISTRIBUTION")
print("=" * 70)

print(df["TARGET"].value_counts())

print("\nPercentage:")
print(
    (df["TARGET"].value_counts(normalize=True) * 100)
    .round(2)
)

# ------------------------------------------------------------
# 4. Duplicate applicants
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("3. DUPLICATE APPLICANTS")
print("=" * 70)

duplicate_ids = df["SK_ID_CURR"].duplicated().sum()

print("Duplicate SK_ID_CURR:", duplicate_ids)

# ------------------------------------------------------------
# 5. Missing values
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("4. MISSING VALUES")
print("=" * 70)

missing_count = df.isnull().sum()

missing_percent = (
    missing_count / len(df) * 100
).round(2)

missing_table = pd.DataFrame({
    "missing_count": missing_count,
    "missing_percent": missing_percent
})

missing_table = missing_table[
    missing_table["missing_count"] > 0
].sort_values(
    "missing_percent",
    ascending=False
)

print(
    "Columns containing missing values:",
    len(missing_table)
)

print("\nTop 30 columns:")
print(
    missing_table.head(30).to_string()
)

# ------------------------------------------------------------
# 6. Constant columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("5. CONSTANT COLUMNS")
print("=" * 70)

constant_columns = []

for column in df.columns:

    unique_values = df[column].nunique(
        dropna=False
    )

    if unique_values <= 1:
        constant_columns.append(column)

print(
    "Number of constant columns:",
    len(constant_columns)
)

print(constant_columns)

# ------------------------------------------------------------
# 7. Data types
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("6. DATA TYPES")
print("=" * 70)

print(df.dtypes.value_counts())

# ------------------------------------------------------------
# 8. Categorical columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("7. CATEGORICAL COLUMNS")
print("=" * 70)

categorical_columns = df.select_dtypes(
    include=["object"]
).columns.tolist()

print(
    "Number of categorical columns:",
    len(categorical_columns)
)

print("\nCategorical columns:")

for column in categorical_columns:

    print(
        f"{column}: "
        f"{df[column].nunique(dropna=True)} unique values"
    )

# ------------------------------------------------------------
# 9. Important financial columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("8. IMPORTANT FINANCIAL FEATURES")
print("=" * 70)

financial_columns = [
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",
    "DAYS_BIRTH",
    "DAYS_EMPLOYED"
]

for column in financial_columns:

    if column in df.columns:

        print("\n" + column)

        print(
            df[column].describe()
        )

# ------------------------------------------------------------
# 10. External source columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("9. EXTERNAL SOURCE FEATURES")
print("=" * 70)

external_columns = [
    column
    for column in df.columns
    if column.startswith("EXT_SOURCE")
]

print(external_columns)

# ------------------------------------------------------------
# 11. ID-like columns
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("10. ID COLUMNS")
print("=" * 70)

id_columns = [
    column
    for column in df.columns
    if "ID" in column
]

print(id_columns)

# ------------------------------------------------------------
# 12. Target sanity checks
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("11. TARGET SANITY CHECK")
print("=" * 70)

check_columns = [
    "NAME_INCOME_TYPE",
    "NAME_CONTRACT_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS",
    "NAME_HOUSING_TYPE"
]

for column in check_columns:

    if column in df.columns:

        print("\n" + column)

        result = pd.crosstab(
            df[column],
            df["TARGET"],
            normalize="index"
        )

        print(
            result.round(3).head(20)
        )

# ------------------------------------------------------------
# 13. Final message
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DATA QUALITY CHECK COMPLETED")
print("=" * 70)
