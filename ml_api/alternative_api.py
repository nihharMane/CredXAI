from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import hashlib
import pandas as pd
import logging
import time
from pathlib import Path
try:
    from .logging_config import configure_logging, install_request_logging, log_prediction_endpoint
except ImportError:
    from logging_config import configure_logging, install_request_logging, log_prediction_endpoint


# ============================================================
# CREDXAI - SIMPLE ALTERNATIVE CREDIT RISK API
# Model-based XAI using Logistic Regression coefficients
# ============================================================

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "simple_alternative_logistic_regression.pkl"

configure_logging()
log = logging.getLogger("credxai.alternative")
model_load_started = time.perf_counter()
try:
    model = joblib.load(MODEL_PATH)
    MODEL_VERSION = f"sha256:{hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()[:12]}"
    log.info("model loaded model=alternative version=%s duration_ms=%.1f", MODEL_VERSION,
             (time.perf_counter() - model_load_started) * 1000)
except Exception:
    log.exception("model loading failed model=alternative path_exists=%s", MODEL_PATH.is_file())
    raise


# ============================================================
# FASTAPI
# ============================================================

@asynccontextmanager
async def lifespan(_app):
    log.info("ML service started service=alternative")
    yield
    log.info("ML service stopped service=alternative")


app = FastAPI(
    title="CredXAI Alternative Credit Risk API",
    description=(
        "Alternative-data credit risk prediction for "
        "thin-file applicants using 8 simple inputs."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
install_request_logging(app, "alternative")

# Allow the deployed React frontend to call this API.
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

class AlternativeCreditApplication(BaseModel):

    age_range: str
    account_tenure_months: float = Field(..., ge=0)
    monthly_income: float = Field(..., gt=0)
    monthly_spending: float = Field(..., ge=0)
    average_balance: float
    overdraft_frequency_percent: float = Field(..., ge=0, le=100)
    bill_payment_consistency_percent: float = Field(..., ge=0, le=100)
    cashflow_stability_percent: float = Field(..., ge=0, le=100)


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

        "model_version": MODEL_VERSION,

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

    log.debug("health check completed service=alternative")

    return {
        "status": "healthy",
        "model_loaded": True,
        "model_version": MODEL_VERSION
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
    if hasattr(model, "named_steps"):
        steps = model.named_steps
        classifier = next((step for step in steps.values() if hasattr(step, "coef_")), None)
        preprocessor = next((step for step in steps.values() if hasattr(step, "get_feature_names_out")), None)
        if preprocessor is not None:
            transformed = preprocessor.transform(data)
            if hasattr(transformed, "toarray"):
                transformed = transformed.toarray()
            transformed = transformed[0]
            feature_names = preprocessor.get_feature_names_out()
        else:
            transformed = data.values[0]
            feature_names = data.columns.tolist()
        coefficients = classifier.coef_[0]
    else:
        transformed = data.values[0]
        feature_names = data.columns.tolist()
        coefficients = model.coef_[0]
    return [{"feature": feature, "contribution": float(contribution)}
            for feature, contribution in zip(feature_names, transformed * coefficients)]

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
        "age_range": "Age range",
        "account_tenure_days": "Account tenure",
        "avg_monthly_income": "Monthly income",
        "avg_monthly_spend": "Monthly spending",
        "avg_balance": "Average balance",
        "overdraft_frequency": "Overdraft frequency",
        "bill_payment_consistency": "Bill payment consistency",
        "cashflow_stability_score": "Cashflow stability",
    }
    for old, new in replacements.items():
        if feature == old:
            return new
        if feature.startswith(old):
            return feature.replace(old, new, 1)
    return feature


# ============================================================
# PREDICTION
# ============================================================

def _build_model_features(application: AlternativeCreditApplication) -> pd.DataFrame:
    """Convert API percentages to the 0–1 ratios used by the trained model."""
    return pd.DataFrame([{
        "age_range": application.age_range,
        "account_tenure_days": application.account_tenure_months * 30,
        "avg_monthly_income": application.monthly_income,
        "avg_monthly_spend": application.monthly_spending,
        "avg_balance": application.average_balance,
        "overdraft_frequency": application.overdraft_frequency_percent / 100,
        "bill_payment_consistency": application.bill_payment_consistency_percent / 100,
        "cashflow_stability_score": application.cashflow_stability_percent / 100,
    }])


@app.post("/predict")
@log_prediction_endpoint("alternative", "alternative")
def predict(
    application: AlternativeCreditApplication
):
    data = _build_model_features(application)

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    default_class_index = list(model.classes_).index(1)
    probability = float(model.predict_proba(data)[0][default_class_index])

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
                "This is a machine-learning-based risk estimate and should support, not replace, human credit decisions."
            )
    }
