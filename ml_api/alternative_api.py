from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import pandas as pd


# ============================================================
# CREDXAI - SIMPLE ALTERNATIVE CREDIT RISK API
# Model-based XAI using Logistic Regression coefficients
# ============================================================

MODEL_PATH = (
    "models/simple_alternative_logistic_regression.pkl"
)

print("=" * 70)
print("CREDXAI - SIMPLE ALTERNATIVE CREDIT RISK API")
print("=" * 70)

print("\nLoading alternative Logistic Regression model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="CredXAI Alternative Credit Risk API",
    description=(
        "Alternative-data credit risk prediction for "
        "thin-file applicants using 8 simple inputs."
    ),
    version="1.0.0",
)


# ============================================================
# INPUT SCHEMA
# ============================================================

class AlternativeCreditApplication(BaseModel):

    age_range: str

    account_tenure_months: float = Field(
        ...,
        ge=0
    )

    monthly_income: float = Field(
        ...,
        gt=0
    )

    monthly_spending: float = Field(
        ...,
        ge=0
    )

    average_balance: float

    overdraft_frequency_percent: float = Field(
        ...,
        ge=0
    )

    bill_payment_consistency_percent: float = Field(
        ...,
        ge=0,
        le=100
    )

    cashflow_stability_percent: float = Field(
        ...,
        ge=0,
        le=100
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "service":
            "CredXAI Alternative Credit Risk API",

        "model":
            "Simplified Alternative Logistic Regression",

        "input_features":
            8,

        "xai":
            "Logistic Regression coefficient based",

        "status":
            "running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True
    }


# ============================================================
# RISK BAND
# ============================================================

def get_risk_band(probability):

    if probability < 0.30:
        return "LOW_RISK"

    elif probability < 0.60:
        return "MEDIUM_RISK"

    else:
        return "HIGH_RISK"


# ============================================================
# MODEL FEATURE CONTRIBUTIONS
# ============================================================

def calculate_feature_contributions(data):

    # --------------------------------------------------------
    # Your alternative model is a Pipeline.
    # It may contain preprocessing + Logistic Regression.
    # --------------------------------------------------------

    if hasattr(model, "named_steps"):

        steps = model.named_steps

        classifier = None
        preprocessor = None

        for name, step in steps.items():

            if hasattr(step, "coef_"):
                classifier = step

            if hasattr(
                step,
                "get_feature_names_out"
            ):
                preprocessor = step

        # ----------------------------------------------------
        # If preprocessing exists
        # ----------------------------------------------------

        if preprocessor is not None:

            transformed = (
                preprocessor.transform(data)
            )

            if hasattr(
                transformed,
                "toarray"
            ):
                transformed = (
                    transformed.toarray()
                )

            transformed = transformed[0]

            feature_names = (
                preprocessor
                .get_feature_names_out()
            )

        else:

            transformed = data.values[0]

            feature_names = (
                data.columns.tolist()
            )

        coefficients = classifier.coef_[0]

    else:

        # ----------------------------------------------------
        # Plain Logistic Regression
        # ----------------------------------------------------

        transformed = data.values[0]

        feature_names = (
            data.columns.tolist()
        )

        coefficients = model.coef_[0]

    # --------------------------------------------------------
    # Contribution
    #
    # contribution =
    # transformed feature × coefficient
    # --------------------------------------------------------

    contributions = (
        transformed * coefficients
    )

    results = []

    for feature, contribution in zip(
        feature_names,
        contributions
    ):

        results.append(
            {
                "feature": feature,
                "contribution": float(
                    contribution
                )
            }
        )

    return results


# ============================================================
# CLEAN FEATURE NAMES
# ============================================================

def clean_feature_name(feature):

    feature = feature.replace(
        "numeric__",
        ""
    )

    feature = feature.replace(
        "categorical__",
        ""
    )

    replacements = {

        "age_range":
            "Age range",

        "account_tenure_days":
            "Account tenure",

        "avg_monthly_income":
            "Monthly income",

        "avg_monthly_spend":
            "Monthly spending",

        "avg_balance":
            "Average balance",

        "overdraft_frequency":
            "Overdraft frequency",

        "bill_payment_consistency":
            "Bill payment consistency",

        "cashflow_stability_score":
            "Cashflow stability",
    }

    for old, new in replacements.items():

        if feature == old:

            return new

        if feature.startswith(old):

            return feature.replace(
                old,
                new,
                1
            )

    return feature


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
def predict(
    application: AlternativeCreditApplication
):

    # --------------------------------------------------------
    # Convert user-friendly inputs into model features
    # --------------------------------------------------------

    data = pd.DataFrame(
        [
            {
                "age_range":
                    application.age_range,

                "account_tenure_days":
                    application.account_tenure_months
                    * 30,

                "avg_monthly_income":
                    application.monthly_income,

                "avg_monthly_spend":
                    application.monthly_spending,

                "avg_balance":
                    application.average_balance,

                "overdraft_frequency":
                    application
                    .overdraft_frequency_percent,

                "bill_payment_consistency":
                    application
                    .bill_payment_consistency_percent
                    / 100,

                "cashflow_stability_score":
                    application
                    .cashflow_stability_percent
                    / 100,
            }
        ]
    )

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    probability = float(
        model.predict_proba(data)[0][1]
    )

    prediction = int(
        probability >= 0.50
    )

    probability_percent = round(
        probability * 100,
        2
    )

    risk_band = get_risk_band(
        probability
    )

    # --------------------------------------------------------
    # ACTUAL MODEL CONTRIBUTIONS
    # --------------------------------------------------------

    contributions = (
        calculate_feature_contributions(data)
    )

    contributions_sorted = sorted(
        contributions,
        key=lambda x: abs(
            x["contribution"]
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # RISK INCREASING
    # --------------------------------------------------------

    increasing = [
        item
        for item in contributions_sorted
        if item["contribution"] > 0
    ]

    # --------------------------------------------------------
    # RISK REDUCING
    # --------------------------------------------------------

    reducing = [
        item
        for item in contributions_sorted
        if item["contribution"] < 0
    ]

    # --------------------------------------------------------
    # TOP FACTORS
    # --------------------------------------------------------

    risk_increasing_factors = []

    for item in increasing[:5]:

        risk_increasing_factors.append(
            {
                "feature":
                    clean_feature_name(
                        item["feature"]
                    ),

                "contribution":
                    round(
                        item["contribution"],
                        4
                    )
            }
        )

    risk_reducing_factors = []

    for item in reducing[:5]:

        risk_reducing_factors.append(
            {
                "feature":
                    clean_feature_name(
                        item["feature"]
                    ),

                "contribution":
                    round(
                        item["contribution"],
                        4
                    )
            }
        )

    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    explanation = []

    if probability >= 0.60:

        explanation.append(
            "The model estimates a high probability of default."
        )

    elif probability >= 0.30:

        explanation.append(
            "The model estimates a moderate probability of default."
        )

    else:

        explanation.append(
            "The model estimates a low probability of default."
        )

    if risk_increasing_factors:

        names = [
            item["feature"]
            for item in
            risk_increasing_factors[:3]
        ]

        explanation.append(
            "The main factors increasing estimated "
            "risk are: "
            + ", ".join(names)
            + "."
        )

    if risk_reducing_factors:

        names = [
            item["feature"]
            for item in
            risk_reducing_factors[:3]
        ]

        explanation.append(
            "The main factors reducing estimated "
            "risk are: "
            + ", ".join(names)
            + "."
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "model_type":
            "ALTERNATIVE_DATA",

        "prediction":
            prediction,

        "default_probability":
            round(
                probability,
                6
            ),

        "default_probability_percent":
            probability_percent,

        "risk_band":
            risk_band,

        "risk_increasing_factors":
            risk_increasing_factors,

        "risk_reducing_factors":
            risk_reducing_factors,

        "explanation":
            explanation,

        "disclaimer":
            (
                "This is a machine-learning-based risk "
                "estimate and should support, not replace, "
                "human credit decisions."
            )
    }