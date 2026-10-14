import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CREDXAI
# Initial Application Feature Dataset
# ============================================================

INPUT_PATH = Path(
    "data/raw/home_credit/application_train.csv"
)

OUTPUT_PATH = Path(
    "data/processed/application_features.csv"
)

print("=" * 70)
print("CREDXAI - APPLICATION FEATURE CREATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load only the columns we actually want
# ------------------------------------------------------------

selected_columns = [
    # Identification / target
    "SK_ID_CURR",
    "TARGET",

    # Financial
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",

    # Demographic / stability
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",

    # Employment / income type
    "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS",
    "NAME_HOUSING_TYPE",

    # Loan type
    "NAME_CONTRACT_TYPE",

    # Ownership
    "FLAG_OWN_CAR",
    "FLAG_OWN_REALTY",
]

print("\nLoading application data...")

df = pd.read_csv(
    INPUT_PATH,
    usecols=selected_columns
)

print("Original rows:", len(df))
print("Original selected columns:", len(df.columns))

# ------------------------------------------------------------
# 2. Convert age into years
# ------------------------------------------------------------

# DAYS_BIRTH is stored as negative days.
df["AGE_YEARS"] = (
    -df["DAYS_BIRTH"] / 365.25
)

# ------------------------------------------------------------
# 3. Convert employment duration into years
# ------------------------------------------------------------

# Home Credit uses 365243 as a special value
# for certain employment situations.
SPECIAL_EMPLOYMENT_VALUE = 365243

df["EMPLOYED_YEARS"] = (
    -df["DAYS_EMPLOYED"] / 365.25
)

# Replace the special value with missing
df.loc[
    df["DAYS_EMPLOYED"] == SPECIAL_EMPLOYMENT_VALUE,
    "EMPLOYED_YEARS"
] = np.nan

# ------------------------------------------------------------
# 4. Create meaningful financial ratios
# ------------------------------------------------------------

# Credit amount relative to income
df["CREDIT_TO_INCOME"] = (
    df["AMT_CREDIT"] /
    df["AMT_INCOME_TOTAL"].replace(0, np.nan)
)

# Annualized annuity relative to income
df["ANNUITY_TO_INCOME"] = (
    df["AMT_ANNUITY"] /
    df["AMT_INCOME_TOTAL"].replace(0, np.nan)
)

# Goods price relative to income
df["GOODS_PRICE_TO_INCOME"] = (
    df["AMT_GOODS_PRICE"] /
    df["AMT_INCOME_TOTAL"].replace(0, np.nan)
)

# Credit amount relative to goods price
df["CREDIT_TO_GOODS_PRICE"] = (
    df["AMT_CREDIT"] /
    df["AMT_GOODS_PRICE"].replace(0, np.nan)
)

# ------------------------------------------------------------
# 5. Family dependency feature
# ------------------------------------------------------------

df["CHILDREN_PER_FAMILY_MEMBER"] = (
    df["CNT_CHILDREN"] /
    df["CNT_FAM_MEMBERS"].replace(0, np.nan)
)

# ------------------------------------------------------------
# 6. Remove raw columns that are no longer needed
# ------------------------------------------------------------

df = df.drop(
    columns=[
        "DAYS_BIRTH",
        "DAYS_EMPLOYED"
    ]
)

# ------------------------------------------------------------
# 7. Save
# ------------------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

# ------------------------------------------------------------
# 8. Report
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FEATURE DATASET CREATED")
print("=" * 70)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\nColumns:")
for column in df.columns:
    print("-", column)

print("\nMissing values:")
print(
    df.isnull()
    .sum()
    .sort_values(ascending=False)
    .head(20)
)

print("\nTarget:")
print(df["TARGET"].value_counts())

print("\nSaved to:")
print(OUTPUT_PATH)

print("\nFeature creation completed.")
