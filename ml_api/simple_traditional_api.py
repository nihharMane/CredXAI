from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
from pathlib import Path
import hashlib
from typing import Literal
import joblib
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
try:
    from .logging_config import configure_logging, install_request_logging, log_prediction_endpoint
except ImportError:
    from logging_config import configure_logging, install_request_logging, log_prediction_endpoint

# ============================================================
# CREDXAI - SIMPLE TRADITIONAL CREDIT RISK API
# Model-based XAI using Logistic Regression coefficients
# ============================================================

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "simple_traditional_logistic_regression.pkl"

configure_logging()
log = logging.getLogger("credxai.traditional")
model_load_started = time.perf_counter()
try:
    model = joblib.load(MODEL_PATH)
    MODEL_VERSION = f"sha256:{hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()[:12]}"
    log.info("model loaded model=traditional version=%s duration_ms=%.1f", MODEL_VERSION,
             (time.perf_counter() - model_load_started) * 1000)
except Exception:
    log.exception("model loading failed model=traditional path_exists=%s", MODEL_PATH.is_file())
    raise


# ============================================================
# FASTAPI
# ============================================================

@asynccontextmanager
async def lifespan(_app):
    log.info("ML service started service=traditional")
    yield
    log.info("ML service stopped service=traditional")


app = FastAPI(
    title="CredXAI Traditional Credit Risk API",
    description=(
        "Traditional credit risk prediction using "
        "12 simple applicant inputs with model-based XAI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
install_request_logging(app, "traditional")


# Allow the deployed CredXAI frontend to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://credxai-frontend.onrender.com", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)


# ============================================================
# INPUT SCHEMA
# ============================================================

class TraditionalCreditApplication(BaseModel):

    model_config = ConfigDict(allow_inf_nan=False)

    age: float = Field(..., ge=18, le=100)

    children: int = Field(..., ge=0)

    family_members: float = Field(..., ge=1)

    income_type: Literal[
        "Working", "Commercial associate", "Pensioner", "State servant",
        "Businessman", "Student", "Unemployed", "Maternity leave"
    ]

    monthly_income: float = Field(..., gt=0, le=1_000_000_000)

    credit_amount: float = Field(..., gt=0, le=9_999_999_999_999.99)

    monthly_installment: float = Field(..., gt=0, le=1_000_000_000)

    goods_price: float = Field(..., gt=0, le=1_000_000_000)

    owns_car: Literal["Y", "N"]

    owns_property: Literal["Y", "N"]

    education: Literal[
        "Secondary / secondary special", "Higher education",
        "Incomplete higher", "Lower secondary", "Academic degree"
    ]

    housing_type: Literal[
        "House / apartment", "With parents", "Municipal apartment",
        "Rented apartment", "Office apartment", "Co-op apartment"
    ]


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "service": "CredXAI Traditional Credit Risk API",
        "model": "Simplified Traditional Logistic Regression",
        "model_version": MODEL_VERSION,
        "input_features": 12,
        "xai": "Logistic Regression coefficient based",
        "status": "running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    log.debug("health check completed service=traditional")

    return {
        "status": "healthy",
        "model_loaded": True,
        "model_version": MODEL_VERSION
    }
@app.get("/cors-check")
def cors_check():
    return {
        "service": "traditional-ml",
        "cors_middleware_configured": True
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

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    # Transform input
    transformed = preprocessor.transform(data)

    # Convert sparse matrix if necessary
    if hasattr(transformed, "toarray"):
        transformed_array = transformed.toarray()[0]
    else:
        transformed_array = transformed[0]

    # Get transformed feature names
    feature_names = preprocessor.get_feature_names_out()

    # Logistic regression coefficients
    coefficients = classifier.coef_[0]

    # Contribution = transformed value × coefficient
    contributions = (
        transformed_array * coefficients
    )

    results = []

    for feature, contribution in zip(
        feature_names,
        contributions
    ):

        results.append(
            {
                "feature": feature,
                "contribution": float(contribution)
            }
        )

    return results


# ============================================================
# MAKE FEATURE NAMES USER FRIENDLY
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

    feature = feature.replace(
        "AGE_YEARS",
        "Age"
    )

    feature = feature.replace(
        "CNT_CHILDREN",
        "Number of children"
    )

    feature = feature.replace(
        "CNT_FAM_MEMBERS",
        "Family members"
    )

    feature = feature.replace(
        "AMT_INCOME_TOTAL",
        "Income"
    )

    feature = feature.replace(
        "AMT_CREDIT",
        "Credit amount"
    )

    feature = feature.replace(
        "AMT_ANNUITY",
        "Monthly installment"
    )

    feature = feature.replace(
        "AMT_GOODS_PRICE",
        "Goods price"
    )

    feature = feature.replace(
        "FLAG_OWN_CAR",
        "Car ownership"
    )

    feature = feature.replace(
        "FLAG_OWN_REALTY",
        "Property ownership"
    )

    feature = feature.replace(
        "NAME_INCOME_TYPE",
        "Income type"
    )

    feature = feature.replace(
        "NAME_EDUCATION_TYPE",
        "Education"
    )

    feature = feature.replace(
        "NAME_HOUSING_TYPE",
        "Housing type"
    )

    return feature


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
@log_prediction_endpoint("traditional", "traditional")
def predict(
    application: TraditionalCreditApplication
):

    # --------------------------------------------------------
    # Convert user input to model features
    # --------------------------------------------------------

    data = pd.DataFrame(
        [
            {
                "AGE_YEARS":
                    application.age,

                "CNT_CHILDREN":
                    application.children,

                "CNT_FAM_MEMBERS":
                    application.family_members,

                "NAME_INCOME_TYPE":
                    application.income_type,

                # Home Credit dataset uses annual income
                "AMT_INCOME_TOTAL":
                    application.monthly_income * 12,

                "AMT_CREDIT":
                    application.credit_amount,

                # Home Credit dataset uses annual annuity
                "AMT_ANNUITY":
                    application.monthly_installment * 12,

                "AMT_GOODS_PRICE":
                    application.goods_price,

                "FLAG_OWN_CAR":
                    application.owns_car.upper(),

                "FLAG_OWN_REALTY":
                    application.owns_property.upper(),

                "NAME_EDUCATION_TYPE":
                    application.education,

                "NAME_HOUSING_TYPE":
                    application.housing_type
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

    # Sort by contribution
    contributions_sorted = sorted(
        contributions,
        key=lambda x: abs(x["contribution"]),
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
    # TOP 5 EACH
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
            x["feature"]
            for x in risk_increasing_factors[:3]
        ]

        explanation.append(
            "The main factors increasing estimated risk are: "
            + ", ".join(names)
            + "."
        )

    if risk_reducing_factors:

        names = [
            x["feature"]
            for x in risk_reducing_factors[:3]
        ]

        explanation.append(
            "The main factors reducing estimated risk are: "
            + ", ".join(names)
            + "."
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "model_type":
            "TRADITIONAL_DATA",

        "model_version": MODEL_VERSION,

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
                "This is a machine-learning-based risk estimate "
                "and should support, not replace, human credit decisions."
            )
    }
