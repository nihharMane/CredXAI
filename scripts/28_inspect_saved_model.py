from pathlib import Path

# ============================================================
# CREDXAI - SAVED MODEL FILE INSPECTION
# ============================================================

MODEL_PATH = Path(
    "models/calibrated_logistic_regression.pkl"
)

print("=" * 70)
print("CREDXAI - SAVED MODEL FILE INSPECTION")
print("=" * 70)

print("\nModel path:")
print(MODEL_PATH)

print("\nFile exists:")
print(MODEL_PATH.exists())

if MODEL_PATH.exists():

    print("\nFile size:")
    print(
        f"{MODEL_PATH.stat().st_size:,} bytes"
    )

    print("\nFile extension:")
    print(MODEL_PATH.suffix)

# ------------------------------------------------------------
# Try joblib
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("TRYING JOBLIB")
print("=" * 70)

try:

    import joblib

    model = joblib.load(
        MODEL_PATH
    )

    print("\nSUCCESS: Model loaded with joblib.")

    print("\nModel type:")
    print(type(model))

    print("\nModel:")
    print(model)

    print("\nAvailable important attributes:")

    attributes = [
        "predict",
        "predict_proba",
        "named_steps",
        "steps",
        "feature_names_in_",
        "classes_",
        "estimator",
        "calibrated_classifiers_"
    ]

    for attribute in attributes:

        print(
            f"{attribute:<30}: "
            f"{hasattr(model, attribute)}"
        )

except Exception as error:

    print("\nJOBLIB LOAD FAILED")

    print(
        "Error type:",
        type(error).__name__
    )

    print(
        "Error:",
        error
    )

print("\n" + "=" * 70)
print("INSPECTION COMPLETED")
print("=" * 70)