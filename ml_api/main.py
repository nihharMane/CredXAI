from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path


# ============================================================
# CREDXAI - ML PREDICTION + EXPLAINABILITY API
# ============================================================

MODEL_PATH = Path("models/calibrated_logistic_regression.pkl")


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="CredXAI ML API",
    description="Credit risk prediction and applicant-specific explainability API",
    version="1.1.0"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading CredXAI model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")


# ============================================================
# REQUEST MODEL
# ============================================================

class CreditApplication(BaseModel):

    NAME_CONTRACT_TYPE: str
    FLAG_OWN_CAR: str
    FLAG_OWN_REALTY: str

    CNT_CHILDREN: float
    AMT_INCOME_TOTAL: float
    AMT_CREDIT: float
    AMT_ANNUITY: float
    AMT_GOODS_PRICE: float

    NAME_INCOME_TYPE: str
    NAME_EDUCATION_TYPE: str
    NAME_FAMILY_STATUS: str
    NAME_HOUSING_TYPE: str

    CNT_FAM_MEMBERS: float
    AGE_YEARS: float
    EMPLOYED_YEARS: float

    CREDIT_TO_INCOME: float
    ANNUITY_TO_INCOME: float
    GOODS_PRICE_TO_INCOME: float
    CREDIT_TO_GOODS_PRICE: float
    CHILDREN_PER_FAMILY_MEMBER: float

    PREVIOUS_APPLICATION_COUNT: float
    PREVIOUS_APPROVED_COUNT: float
    PREVIOUS_REFUSED_COUNT: float
    PREVIOUS_CANCELLED_COUNT: float

    PREVIOUS_AVG_APPLICATION_AMOUNT: float
    PREVIOUS_AVG_CREDIT_AMOUNT: float
    PREVIOUS_MAX_CREDIT_AMOUNT: float
    PREVIOUS_AVG_DOWN_PAYMENT: float
    PREVIOUS_AVG_GOODS_PRICE: float
    PREVIOUS_AVG_ANNUITY: float

    PREVIOUS_APPROVAL_RATE: float
    PREVIOUS_REFUSAL_RATE: float
    PREVIOUS_CREDIT_TO_APPLICATION: float

    INSTALLMENT_COUNT: float
    UNIQUE_PREVIOUS_LOANS: float
    AVG_PAYMENT_DELAY: float
    MAX_PAYMENT_DELAY: float
    AVG_PAYMENT_RATIO: float

    TOTAL_INSTALLMENT_AMOUNT: float
    TOTAL_PAYMENT_AMOUNT: float
    AVG_INSTALLMENT_AMOUNT: float
    AVG_PAYMENT_AMOUNT: float

    LATE_PAYMENT_COUNT: float
    SEVERE_LATE_PAYMENT_COUNT: float
    LATE_PAYMENT_RATIO: float
    SEVERE_LATE_PAYMENT_RATIO: float
    OVERALL_PAYMENT_RATIO: float

    CREDIT_CARD_RECORD_COUNT: float
    CREDIT_CARD_COUNT: float
    AVG_CARD_BALANCE: float
    MAX_CARD_BALANCE: float
    AVG_CREDIT_LIMIT_x: float
    MAX_CREDIT_LIMIT: float
    AVG_CREDIT_UTILIZATION: float
    MAX_CREDIT_UTILIZATION: float

    AVG_CARD_PAYMENT: float
    TOTAL_CARD_PAYMENT: float
    AVG_CARD_PAYMENT_RATIO: float
    TOTAL_DRAWINGS: float
    AVG_DRAWINGS: float
    TOTAL_ATM_DRAWINGS: float
    TOTAL_POS_DRAWINGS: float
    TOTAL_OTHER_DRAWINGS: float
    AVG_DRAWING_COUNT: float
    TOTAL_DRAWING_COUNT: float
    AVG_DPD: float
    MAX_DPD: float
    DPD_COUNT: float
    DPD_RATIO: float

    POS_CASH_RECORD_COUNT: float
    POS_CASH_LOAN_COUNT: float
    AVG_INSTALLMENT_COUNT: float
    AVG_INSTALLMENTS_FUTURE: float
    AVG_POS_DPD: float
    MAX_POS_DPD: float
    POS_DPD_COUNT: float
    POS_COMPLETED_COUNT: float
    POS_ACTIVE_COUNT: float
    POS_DPD_RATIO: float
    POS_COMPLETED_RATIO: float
    POS_ACTIVE_RATIO: float

    BUREAU_CREDIT_COUNT: float
    UNIQUE_BUREAU_CREDITS: float
    ACTIVE_CREDIT_COUNT: float
    CLOSED_CREDIT_COUNT: float
    AVG_DAYS_CREDIT: float
    MIN_DAYS_CREDIT: float
    AVG_CREDIT_DAY_OVERDUE: float
    MAX_CREDIT_DAY_OVERDUE: float
    OVERDUE_CREDIT_COUNT: float
    OVERDUE_AMOUNT_COUNT: float
    TOTAL_OVERDUE_AMOUNT: float
    MAX_OVERDUE_AMOUNT: float
    AVG_CREDIT_AMOUNT: float
    TOTAL_CREDIT_AMOUNT: float
    TOTAL_CREDIT_DEBT: float
    AVG_CREDIT_DEBT: float
    TOTAL_CREDIT_LIMIT: float
    AVG_CREDIT_LIMIT_y: float
    AVG_CREDIT_ANNUITY: float
    TOTAL_CREDIT_PROLONG: float
    ACTIVE_CREDIT_RATIO: float
    OVERDUE_CREDIT_RATIO: float
    OVERDUE_AMOUNT_RATIO: float
    DEBT_TO_CREDIT_RATIO: float
    CREDIT_LIMIT_UTILIZATION: float


# ============================================================
# RISK BAND
# ============================================================

def get_risk_band(probability):

    if probability < 0.10:
        return "LOW_RISK"

    elif probability < 0.30:
        return "MEDIUM_RISK"

    return "HIGH_RISK"


# ============================================================
# EXPLAINABILITY
# ============================================================

def get_explainability(X):

    # CalibratedClassifierCV contains fitted classifiers.
    calibrated_classifier = model.calibrated_classifiers_[0]

    # Get original pipeline
    pipeline = calibrated_classifier.estimator

    # Get preprocessing pipeline
    preprocessor = pipeline.named_steps["preprocessor"]

    # Get Logistic Regression classifier
    classifier = pipeline.named_steps["classifier"]

    # Transform applicant using exactly the same preprocessing
    X_transformed = preprocessor.transform(X)

    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()

    # Feature names after preprocessing
    feature_names = preprocessor.get_feature_names_out()

    # Logistic regression coefficients
    coefficients = classifier.coef_[0]

    # Applicant-specific contribution
    contributions = X_transformed[0] * coefficients

    explanation_df = pd.DataFrame({
        "FEATURE": feature_names,
        "VALUE": X_transformed[0],
        "COEFFICIENT": coefficients,
        "CONTRIBUTION": contributions
    })

    # Factors increasing risk
    positive = (
        explanation_df[
            explanation_df["CONTRIBUTION"] > 0
        ]
        .sort_values(
            "CONTRIBUTION",
            ascending=False
        )
        .head(5)
    )

    # Factors reducing risk
    negative = (
        explanation_df[
            explanation_df["CONTRIBUTION"] < 0
        ]
        .sort_values(
            "CONTRIBUTION",
            ascending=True
        )
        .head(5)
    )

    risk_increasing_factors = []

    for _, row in positive.iterrows():

        risk_increasing_factors.append({
            "feature": row["FEATURE"],
            "contribution": round(
                float(row["CONTRIBUTION"]), 4
            )
        })

    risk_reducing_factors = []

    for _, row in negative.iterrows():

        risk_reducing_factors.append({
            "feature": row["FEATURE"],
            "contribution": round(
                float(row["CONTRIBUTION"]), 4
            )
        })

    return (
        risk_increasing_factors,
        risk_reducing_factors
    )


# ============================================================
# HUMAN-READABLE EXPLANATION
# ============================================================

def create_explanation(
    application,
    probability,
    risk_band
):

    explanations = []

    # Risk level
    if risk_band == "LOW_RISK":

        explanations.append(
            "The applicant has a low estimated probability of default."
        )

    elif risk_band == "MEDIUM_RISK":

        explanations.append(
            "The applicant has a moderate estimated probability of default."
        )

    else:

        explanations.append(
            "The applicant has a high estimated probability of default."
        )

    # Credit-to-income
    if application.CREDIT_TO_INCOME > 3:

        explanations.append(
            "The requested credit amount is high compared with the applicant's income."
        )

    elif application.CREDIT_TO_INCOME > 2:

        explanations.append(
            "The requested credit amount is relatively high compared with income."
        )

    else:

        explanations.append(
            "The requested credit amount is relatively moderate compared with income."
        )

    # Late payment
    if application.LATE_PAYMENT_RATIO > 0:

        explanations.append(
            f"Late-payment activity was observed with a "
            f"late-payment ratio of {application.LATE_PAYMENT_RATIO:.2f}."
        )

    else:

        explanations.append(
            "No late installment-payment ratio was observed."
        )

    # Previous applications
    if application.PREVIOUS_APPLICATION_COUNT > 0:

        approved = application.PREVIOUS_APPROVED_COUNT

        explanations.append(
            f"{int(application.PREVIOUS_APPLICATION_COUNT)} "
            f"previous application(s) are available, including "
            f"{int(approved)} approved application(s)."
        )

    else:

        explanations.append(
            "No previous application history was provided."
        )

    # Debt
    if application.DEBT_TO_CREDIT_RATIO > 0.5:

        explanations.append(
            "Existing debt represents a relatively high proportion of available credit."
        )

    return explanations


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "application": "CredXAI ML API",
        "status": "running",
        "version": "1.1.0"
    }


# ============================================================
# MODEL HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True
    }


# ============================================================
# PREDICTION + EXPLAINABILITY
# ============================================================

@app.post("/predict")
def predict(application: CreditApplication):

    # --------------------------------------------------------
    # Convert request to DataFrame
    # --------------------------------------------------------

    data = application.model_dump()

    X = pd.DataFrame([data])

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    probability = model.predict_proba(X)[0][1]

    probability_percent = probability * 100

    risk_band = get_risk_band(probability)

    # --------------------------------------------------------
    # Explainability
    # --------------------------------------------------------

    (
        risk_increasing_factors,
        risk_reducing_factors
    ) = get_explainability(X)

    # --------------------------------------------------------
    # Human-readable explanation
    # --------------------------------------------------------

    explanation = create_explanation(
        application,
        probability,
        risk_band
    )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "default_probability":
            round(float(probability), 6),

        "default_probability_percent":
            round(float(probability_percent), 2),

        "risk_band":
            risk_band,

        "risk_increasing_factors":
            risk_increasing_factors,

        "risk_reducing_factors":
            risk_reducing_factors,

        "explanation":
            explanation,

        "disclaimer":
            "This is a machine-learning-based risk estimate and should support, not replace, human credit decisions."
    }