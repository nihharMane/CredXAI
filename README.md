# CredXAI: Full-Stack Explainable AI Credit Risk Platform

CredXAI is a local decision-support prototype for exploring traditional Home Credit features and an alternative behavioral-data Logistic Regression model. It returns model scores, rule-based risk bands, and signed coefficient contributions. Neither model is validated for lending decisions; the alternative model has only 27 labeled profiles, and the traditional model's current score is poorly calibrated in cross-validation.

## Applicant Workflow — Current Implementation Scope

The applicant-facing application stays focused on the real application journey: a professional landing page, authenticated applicant dashboard, model-specific loan application fields, server-backed predictions, saved results and explanations, downloadable PDF reports, and account-scoped application history. The dashboard uses a three-column layout on wide screens for the application form, returned risk overview, and saved assessment/history summary; it stacks these sections on smaller screens.

The applicant UI does not include model evaluation, model comparison, or model performance metric pages. Training and evaluation scripts, saved metrics, and research notes remain available in the repository for internal development and oral assessment preparation. Predictions and explanations must come from the active ML APIs, while PDF reports are built from the authenticated saved application detail response; the UI does not substitute mock scores or invented rationales.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   React + Vite Frontend     |
                      |   (Tailwind CSS, Port 5173) |
                      +--------------+--------------+
                                     |
                                     | HTTP Proxy (/api)
                                     v
                      +-----------------------------+
                      | Spring Boot 4.1.1 Backend   |
                      |    (Security, JWT, Port 8080)|
                      +-------+-------------+-------+
                              |             |
                 +------------+             +------------+
                 v                                       v
    +------------------------+              +------------------------+
    | Traditional ML API     |              | Alternative ML API     |
    | (FastAPI, Port 8002)   |              | (FastAPI, Port 8001)   |
    | Home Credit Regressor  |              | Behavioral Regressor   |
    +------------------------+              +------------------------+
                 \                                       /
                  +------------------+------------------+
                                     |
                                     v
                            +-----------------+
                            | MySQL Database  |
                            | (Port 3306)     |
                            +-----------------+
```

---

## Prerequisites

Before starting the application, ensure the following are installed:
1. **Java JDK 21+** (e.g., OpenJDK 21 or Oracle JDK 21/23)
2. **Apache Maven 3.9+** (or use the included wrapper if present)
3. **Python 3.10+** (with virtual environment support)
4. **Node.js 20+** and **npm 10+**
5. **MySQL 8.0+**

---

## Step 1: MySQL Database Setup

1. Start your local MySQL server on port `3306`.
2. Connect to MySQL as root and create the database `credxai`:
   ```sql
   CREATE DATABASE credxai;
   ```
3. Set DB_USERNAME, DB_PASSWORD, and JWT_SECRET in the backend terminal environment. The backend defaults to database credxai on localhost:3306; do not put credentials in source files.
   *(Flyway automatically applies all pending versioned migrations at backend startup.)*

---

## Step 2: Set Up Python ML Microservices

1. Navigate to the project root:
   ```bash
   cd D:\CredXAI
   ```
2. Activate or create a virtual environment:
   ```bash
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1

   # Or create new:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install fastapi uvicorn scikit-learn pandas numpy joblib
   ```
3. Start the **Alternative Data ML Microservice** (Port 8001):
   ```bash
   uvicorn ml_api.alternative_api:app --host 127.0.0.1 --port 8001
   ```
4. In a separate terminal, start the **Traditional Credit ML Microservice** (Port 8002):
   ```bash
   cd D:\CredXAI
   .\.venv\Scripts\Activate.ps1
   uvicorn ml_api.simple_traditional_api:app --host 127.0.0.1 --port 8002
   ```

---

## Step 3: Start Spring Boot Backend

1. Navigate to the backend directory:
   ```bash
   cd D:\CredXAI\credxai-backend
   ```

   Set these values in the same PowerShell terminal before running Maven:
      $env:DB_URL = 'jdbc:mysql://localhost:3306/credxai'
      $env:DB_USERNAME = 'root'
      $securePassword = Read-Host -AsSecureString 'Local MySQL password'
      $env:DB_PASSWORD = [System.Net.NetworkCredential]::new('', $securePassword).Password
      $env:JWT_SECRET = (1..4 | ForEach-Object { [guid]::NewGuid().ToString('N') }) -join ''

2. Compile and run the Spring Boot application:
   ```bash
   mvn spring-boot:run
   ```
   The backend will start on `http://localhost:8080`.
   - Health endpoint: `http://localhost:8080/api/auth/health` (Public)
   - Prediction endpoints: `http://localhost:8080/api/predictions/**` (Requires JWT Bearer header)
   - History endpoint: `http://localhost:8080/api/predictions/history` (Requires JWT Bearer header)

---

## Step 4: Start React + Vite Frontend

1. Navigate to the frontend directory:
   ```bash
   cd D:\CredXAI\frontend
   ```
2. Install dependencies (if setting up on a new laptop):
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend runs on http://localhost:5173. The local .env uses a relative API base so Vite proxies /api to Spring Boot at http://localhost:8080; local ML health checks use ports 8001 and 8002.

---

## Running Automated Tests

- **Backend tests:**
  ```bash
  cd D:\CredXAI\credxai-backend
  mvn test
  ```
- **Frontend build test:**
  ```bash
  cd D:\CredXAI\frontend
  npm run build
  ```

---

## Key Features

- **Explainable AI (XAI):** Linear feature attributions display both risk-increasing and risk-reducing factors with normalized waterfall graphs.
- **Dual Underwriting Modes:**
  - *Traditional Model:* 12 applicant inputs mapped to Home Credit features; labels originate from Home Credit's `TARGET` field.
  - *Alternative Model:* Eight profile-derived inputs. The active training script reads `credit_profiles.parquet`; it does not consume `transactions_IN.parquet`.
- **Account isolation:** The authenticated JWT identity scopes assessment history. The included roles are not used for role-based authorization.

---

## Verified Local Architecture and API

| Component | Local address | Entry point or route |
|---|---|---|
| React/Vite | `http://localhost:5173` | `frontend/src` |
| Spring Boot | `http://localhost:8080` | `credxai-backend` |
| MySQL | `localhost:3306` | database `credxai` |
| Alternative FastAPI | `http://127.0.0.1:8001` | `ml_api.alternative_api:app` |
| Traditional FastAPI | `http://127.0.0.1:8002` | `ml_api.simple_traditional_api:app` |

The frontend sends `/api` requests through the Vite proxy to Spring Boot. Dashboard health checks use `/ml-alt` and `/ml-trad` proxy paths. Spring Boot calls the two ML services directly. `ml_api/main.py` is a legacy, unused serving entry point; do not use it for the current application flow.

### Endpoints

- `POST /api/auth/register` and `POST /api/auth/login` — public registration and login.
- `GET /api/auth/health` — public backend and database readiness check.
- `POST /api/predictions/traditional` and `POST /api/predictions/alternative` — JWT required; validates inputs, calls the selected ML API, and stores the assessment under the authenticated email.
- `GET /api/predictions/history` — JWT required; returns records for the authenticated user only.
- `GET /api/predictions/history/{applicationId}` — JWT required; returns one saved record only when it belongs to the authenticated user.
- `GET /health` — each FastAPI service reports model readiness and the loaded artifact fingerprint.
- `POST /predict` — each FastAPI service's prediction endpoint; normally called by Spring Boot.

Prediction requests use JSON fields matching the form DTOs. Traditional requires `age`, `children`, `family_members`, `income_type`, `monthly_income` (INR/month), `credit_amount` (INR), `monthly_installment` (INR/month), `goods_price` (INR), `owns_car`, `owns_property`, `education`, `housing_type`, plus `purpose`, `existing_monthly_debt` (INR/month), and a self-reported repayment-history summary. Alternative requires `age_range`, `account_tenure_months`, `monthly_income`, `monthly_spending`, `average_balance`, the three behavior percentages, `loan_amount`, `purpose`, existing monthly debt, and repayment-history summary. The backend explicitly sends only the existing model features to FastAPI; contextual amount, purpose, debt, and repayment-history fields stay in the saved application record.

Successful prediction responses retain the ML response fields and add `application_id`, `application_status`, `requested_loan_amount`, `existing_monthly_debt`, `repayment_history`, `purpose`, `assessment_timestamp`, and `model_version`. The history detail endpoint returns the saved explanation JSON for that owned application; the history list excludes that larger field.

Assessment inputs and stored context include requested amount, purpose, existing monthly debt obligations, and a self-reported repayment-history summary. The traditional score uses the requested credit amount but does not use the separate existing-debt field, self-reported repayment status, or loan purpose. The alternative model does not use requested amount, existing debt, repayment status, or purpose in its score. Those values are saved for application context and are not silently represented as model features. The traditional form's proposed EMI is a model input; the reported existing debt is separate. Alternative bill-payment consistency is not a verified credit-bureau repayment record.

The alternative form calculates overdraft frequency from months with an overdraft out of the last 12 months, and bill-payment consistency from on-time bills divided by all bills in that period. The API converts these displayed percentages to the 0–1 ratios used by the trained model; its eight feature names and order remain unchanged. `cashflow_stability_score` is copied directly from the source profile by the training preparation pipeline. The repository does not define how that external provider derives the score, so the form accepts only a verified profile score and warns applicants not to estimate it.

Flyway `V1` creates the base schema. `V2` stores amount and purpose, `V3` stores a model artifact fingerprint, `V4` stores existing monthly debt, `V5` stores prediction explanation details, and `V6` stores a repayment-history summary. All additions are nullable for compatibility with older rows. Keep applied migrations immutable.

### Local observability and privacy

The React client, Spring Boot API, and both active FastAPI services emit operational logs without recording credentials, authorization headers, or applicant form values. Spring and FastAPI include validated `X-Correlation-ID` values in response headers and log context; Spring forwards the same ID to the selected ML service. If an incoming ID is malformed, the service replaces it with a generated ID. Set `CREDXAI_LOG_LEVEL=DEBUG` for local diagnostics; the default is `INFO`. Frontend debug logs are enabled only in Vite development builds.

## Model Methodology and Measured Results

### Traditional model

The active API loads `models/simple_traditional_logistic_regression.pkl`, trained by `scripts/40_train_simple_traditional_logistic.py`. It uses 12 Home Credit inputs, median imputation and scaling for numeric features, most-frequent imputation and one-hot encoding for categorical features, and Logistic Regression with `class_weight="balanced"`. The target is Home Credit's `TARGET` (payment difficulty/default-related outcome, value 1). The form asks for monthly income and EMI, then the API multiplies both by 12 to match the dataset's annual income and annuity units.

Read-only five-fold stratified out-of-fold evaluation of the active model artifact, run 2026-10-20 on the 307,511-row processed dataset, produced: accuracy 0.5877, precision 0.1156, recall 0.6179, F1 0.1948, ROC-AUC 0.6369, and Brier score 0.2363. Confusion matrix at 0.50 was `[[165372, 117314], [9485, 15340]]` (rows: actual 0/1; columns: predicted 0/1). The positive rate was 8.07%; a constant-rate Brier reference is 0.0742. The active model's Brier score is worse, so its raw outputs should not be presented as calibrated probabilities.

### Alternative model

The active API loads `models/simple_alternative_logistic_regression.pkl`. `scripts/34_prepare_alternative_model_data.py` maps `credit_outcome` values `good` to 0 and `bad` to 1, excluding other/indeterminate labels; `scripts/38_prepare_simple_alternative.py` selects eight features. Its training data contains 27 rows (18 good and 9 bad). The active model's five-fold stratified out-of-fold evaluation, run 2026-10-20, produced accuracy, precision, recall, F1, and ROC-AUC of 1.0000, Brier score 0.0343, and confusion matrix `[[18, 0], [0, 9]]`. These perfect-looking metrics on 27 examples are extremely uncertain and are not evidence of generalization. The target's provenance is not established in the project code. Although `transactions_IN.parquet` is inspected and other scripts aggregate transactions, the active simple model is trained from `credit_profiles.parquet` features; transaction rows do not feed the serving model.

These results are not a fair head-to-head comparison: datasets, targets, sizes, and feature sets differ. The APIs currently map raw `predict_proba` outputs to low/moderate/high labels using fixed 0.30 and 0.60 thresholds. Those bands are prototype heuristics, not validated lending cutoffs. Contributions are transformed feature values multiplied by Logistic Regression coefficients; they indicate signed contributions to model log-odds, exclude the intercept, and are associations rather than causes. They are not percentage-point changes.

## Local Startup and Shutdown (PowerShell)

Use one PowerShell terminal per service. Start in the repository root unless a command changes directory.

1. Check for a MySQL service and port:

   ```powershell
   Get-Service *mysql* | Select-Object Status, Name
   Test-NetConnection localhost -Port 3306
   ```

   If MySQL is installed as a Windows service but stopped, start its actual service name from an elevated PowerShell: `Start-Service -Name <service-name>`. Create the local database once if it does not exist: `CREATE DATABASE credxai;`. Do not drop or reset a database.

2. Activate the project Python environment and start Alternative ML:

   ```powershell
   Set-Location D:\CredXAI
   .\.venv\Scripts\Activate.ps1
   python -m uvicorn ml_api.alternative_api:app --host 127.0.0.1 --port 8001
   ```

3. In a second PowerShell, start Traditional ML:

   ```powershell
   Set-Location D:\CredXAI
   .\.venv\Scripts\Activate.ps1
   python -m uvicorn ml_api.simple_traditional_api:app --host 127.0.0.1 --port 8002
   ```

4. In a third PowerShell, supply local backend settings and start Spring Boot:

   ```powershell
   Set-Location D:\CredXAI\credxai-backend
   $env:DB_URL = 'jdbc:mysql://localhost:3306/credxai'
   $env:DB_USERNAME = 'root'
   $securePassword = Read-Host -AsSecureString 'Local MySQL password'
   $env:DB_PASSWORD = [System.Net.NetworkCredential]::new('', $securePassword).Password
   $env:JWT_SECRET = (1..4 | ForEach-Object { [guid]::NewGuid().ToString('N') }) -join ''
   .\mvnw.cmd spring-boot:run
   ```

   Flyway applies pending migrations on startup. The secret generated above is for local development only; do not commit or reuse it.

5. In a fourth PowerShell, start the frontend:

   ```powershell
   Set-Location D:\CredXAI\frontend
   npm ci
   npm run dev
   ```

6. Check health without exposing credentials:

   ```powershell
   Invoke-RestMethod http://localhost:8080/api/auth/health
   Invoke-RestMethod http://127.0.0.1:8001/health
   Invoke-RestMethod http://127.0.0.1:8002/health
   ```

   Open `http://localhost:5173`. Stop each process with `Ctrl+C`; leave MySQL running if other local work uses it.

For a fresh environment, create `.venv` and install the pinned dependencies with `python -m pip install -r requirements.txt`. The existing model pickle files must be present under `models/`; the serving APIs resolve them relative to the repository, independent of the current directory.

## API and Frontend Checks

```powershell
Set-Location D:\CredXAI\credxai-backend
.\mvnw.cmd test
Set-Location D:\CredXAI\frontend
npm run build
Set-Location D:\CredXAI
.\.venv\Scripts\python.exe -m compileall -q ml_api
```

The default backend suite runs request-boundary validation tests without MySQL. A full app context and Flyway migration check is available when MySQL and backend environment variables are set: run `.\mvnw.cmd -Dcredxai.integration=true test` from `credxai-backend`. The frontend currently has a build script but no automated component test suite.

## Security and Known Limitations

- Passwords are BCrypt-hashed. The backend reads database and JWT secrets from environment variables; no secrets belong in source control. JWTs are stored in browser local storage, so this prototype should only run on trusted local environments and still needs a stronger browser-token storage strategy before production use.
- Prediction, history, and application-detail routes require JWT authentication. Detail retrieval queries by both application ID and the authenticated user's ID. PDF reports are downloaded from the authenticated saved application detail and stored model response; older records without saved explanation data cannot produce complete reports.
- Current roles are embedded in JWTs but not used for role-based authorization. Only predictions routes are protected by the current security rule; do not add sensitive routes without explicit authorization rules.
- The health endpoint now checks the backend's database connection. ML health reports readiness of the loaded artifact, not model quality or calibration.
- The application stores score, risk band, status, model fingerprint, requested amount, purpose, existing monthly debt, self-reported repayment summary, timestamp, and the returned explanation details. It does not retain all applicant inputs, so a historical score cannot currently be fully reproduced from the database.
- The frontend generates a downloadable PDF from saved application and prediction data. Independent fairness evaluation, validated threshold selection, real bureau integration, and a human lending workflow are not implemented. The prototype does not approve or reject loans.
- The alternative target provenance is unclear and the labeled sample is only 27 rows. The traditional model's current raw outputs perform worse on Brier score than a constant base-rate reference in the measured cross-validation.

## Industrial Oral Assessment: Short Answers

- **Why Logistic Regression?** It is a transparent binary-classification baseline. Its coefficients can be combined with transformed input features to show signed log-odds contributions; it remains a prototype, not a validated lending model.
- **What is ROC-AUC?** It measures ranking of positive above negative cases across thresholds. It does not assess probability calibration or define a safe lending cutoff.
- **Precision and recall?** Precision is the share of predicted positives that are actually positive; recall is the share of actual positives found. The decision threshold changes their trade-off.
- **F1?** The harmonic mean of precision and recall. It does not account for calibration or business costs.
- **What is Brier score?** Mean squared error between probability estimates and binary outcomes; lower is better. The traditional model's measured score is worse than the constant prevalence reference.
- **What does calibration mean?** Among cases given a probability near 20%, roughly 20% should experience the target outcome. The current traditional model does not meet this standard in the measured result.
- **How does JWT work here?** Login returns a signed token whose subject is the normalized email. The frontend sends it as a Bearer token; Spring validates it and uses the subject to scope saved history.
- **Why Flyway?** Versioned SQL migrations evolve schemas incrementally. Applied migrations should remain unchanged so existing databases can move forward safely.
- **Why two ML services?** The traditional and alternative pipelines have different input schemas and feature preprocessing. Keeping separate APIs makes those contracts explicit, but their metrics are not directly comparable.
- **What do the explanations mean?** They show signed contributions to the model's log-odds score for the adverse class. They are not causal explanations, advice, or guarantees about changing an outcome.
- **Can CredXAI approve a loan?** No. It is a decision-support prototype; its outputs are not validated or suitable as an automatic lending decision.
- **What is a REST API?** It exposes resources and operations through HTTP methods and JSON. The React app calls Spring Boot, which validates and authenticates the request before calling the matching ML service.
- **How are database records related?** One user can own many credit applications. Each application has a non-null `user_id` foreign key; detail lookups filter by both application ID and the authenticated user's ID.
- **What does the alternative model measure?** Its training script maps source profile `credit_outcome` values `good` and `bad` to binary labels. The code does not establish who produced those labels or how they were validated.
- **What fairness evidence is available?** None that supports a fairness claim. The small alternative sample is inadequate for subgroup conclusions, and the traditional model requires independent fairness and impact review.

## Database, Authentication, and Configuration Reference

The `users` table contains ID, unique email, full name, BCrypt password hash, and role. `credit_applications.user_id` references `users.id`. Each application stores score, risk band, model type and artifact fingerprint, status, creation time, requested amount, purpose, existing monthly debt, self-reported repayment summary, and the model's explanation response. Full form values are not stored.

Registration normalizes email and hashes passwords with BCrypt. Login returns a signed JWT with email as subject and role as a claim. The frontend sends it in an `Authorization: Bearer` header. The JWT filter establishes the principal; prediction and history services use its email to associate or retrieve records. The role is not currently used to grant different permissions.

| Variable | Purpose | Local default or requirement |
|---|---|---|
| `DB_URL` | JDBC connection | `jdbc:mysql://localhost:3306/credxai` |
| `DB_USERNAME` | MySQL user | `root` in local properties; prefer a dedicated local account |
| `DB_PASSWORD` | MySQL password | Required from environment |
| `JWT_SECRET` | HMAC signing key | Required; minimum 32 UTF-8 bytes |
| `JWT_EXPIRATION` | Token lifetime in milliseconds | `86400000` (one day) |
| `ML_ALTERNATIVE_URL` | Spring-to-ML URL | `http://127.0.0.1:8001` |
| `ML_TRADITIONAL_URL` | Spring-to-ML URL | `http://127.0.0.1:8002` |
| `PORT` | Spring server port | `8080` |
| `VITE_API_BASE_URL` | Frontend API base | Empty for the Vite `/api` proxy |
| `VITE_ALTERNATIVE_ML_URL` | Browser health-check URL | `/ml-alt` through Vite proxy |
| `VITE_TRADITIONAL_ML_URL` | Browser health-check URL | `/ml-trad` through Vite proxy |

Do not put secret values in `.env.example`, README, logs, or Git. `application-prod.properties` remains deployment-specific and was not changed as part of this local-first work.

## Demo Checklist

1. Start MySQL, both ML APIs, Spring Boot, and Vite using the PowerShell steps above. Confirm each health response before opening the UI.
2. Register a demo account and sign in. Use synthetic values or data you are authorized to use.
3. Submit a traditional assessment. Show that monthly income and proposed EMI are entered in INR/month, while requested amount, separate existing debt, purpose, and self-reported repayment status are recorded.
4. Review the result, its application ID, artifact fingerprint, saved context, adverse-outcome score, heuristic band, and signed log-odds factors.
5. Open the report from assessment history and download the PDF. Confirm it contains the saved application fields, returned model probability/category, model version, and only the explanations stored with that prediction.
6. Submit an alternative assessment and explain that amount, purpose, debt, and self-reported repayment status are saved but do not influence the current alternative model.
7. Review evaluation scripts, saved metrics, and research notes from the repository when preparing for technical verification; they are intentionally absent from the applicant UI.
8. End by stating that the system is a prototype and does not approve or reject applications.

## Troubleshooting

- **MySQL connection refused:** Check the actual Windows service name with `Get-Service *mysql*` and verify `Test-NetConnection localhost -Port 3306`. Start the installed service from an elevated shell if it is stopped. Do not drop the database to resolve a connection problem.
- **Flyway or Hibernate schema validation fails:** Check that `DB_URL` points to the intended local `credxai` database and that pending `V2`–`V6` migrations ran. Do not edit an applied migration or disable schema validation to mask a mismatch.
- **Spring Boot will not start:** Confirm `DB_PASSWORD` and a `JWT_SECRET` with at least 32 bytes are set in that terminal; check port 8080 and the required Java 21-compatible toolchain.
- **ML API fails while loading a model:** Run commands from any folder; the service now resolves artifacts relative to the repository. Confirm the named `.pkl` file exists in `models/` and dependencies from `requirements.txt` are installed.
- **Prediction returns service unavailable:** Check the corresponding `/health` endpoint and backend ML URL. The backend returns a safe 503 when the ML service is absent or returns an invalid schema; it does not fabricate a score.
- **Frontend cannot reach backend or ML health:** Keep Vite on port 5173 and backend on 8080; the local Vite proxy paths are `/api`, `/ml-alt`, and `/ml-trad`. Restart Vite after changing its environment file.
- **History or report is unavailable:** Sign in again if the JWT expired. A report is returned only for an application owned by the current account; old rows without stored explanation details cannot produce a complete report.

## Training and Evaluation Scripts

Feature preparation scripts live in `scripts/`. The active simple Logistic Regression training entry points are `scripts/40_train_simple_traditional_logistic.py` and `scripts/39_train_simple_alternative_logistic.py`; each writes its corresponding file under `models/`. Review the input dataset, targets, and outputs before running these scripts because they overwrite model artifacts. The current evaluation metrics documented above were computed without retraining or changing those artifacts. Raw data, processed CSVs, outputs, and model binaries are local assets and are not all tracked in Git.
