# Project Plan: Using Machine Learning to Support Business Decision-Making in Small Enterprises

## Core Question

Can a simple AI model help small businesses make better decisions?

## Dataset

- Source: https://www.kaggle.com/datasets/mohammadtalib786/retail-sales-dataset/data
- Local path target: data/retail_sales_dataset.csv

## Phase 1: Data Processing

### Objectives

- Handle missing values.
- Convert date into time features.
- Normalize numeric features when needed.

### Implementation Status

- [x] Preprocessing module created in backend/src/data/preprocessing.py.
- [x] Date parsing and feature engineering added: month, day, dayofweek, is_weekend.
- [x] Missing value handling and column inference implemented.
- [ ] Validate preprocessing with real Kaggle dataset locally.

### Outputs

- Clean feature matrix for model training.
- Inference helper for product/date input.

## Phase 2: Build ML Model

### Objectives

- Train on past sales.
- Predict future sales (next-day per product).
- Evaluate with MAE and RMSE.

### Implementation Status

- [x] Linear Regression pipeline implemented.
- [x] Random Forest pipeline implemented.
- [x] Time-based train/test split implemented.
- [x] Evaluation module implemented (MAE, RMSE).
- [x] Best-model selection implemented.
- [x] Artifact persistence implemented (model + metrics).
- [ ] Run training on real dataset and capture benchmark metrics.

### Commands

- Train: python -m src.train --dataset ../data/retail_sales_dataset.csv
- Run API: uvicorn src.api.app:app --reload --port 8000

## Phase 3: Decision Support Prototype

### Objectives

- Backend in Python (FastAPI).
- Frontend in Angular.
- Input: product and date.
- Output: predicted sales and stock suggestion.

### Implementation Status

- [x] FastAPI app scaffolded in backend/src/api/app.py.
- [x] Prediction endpoint implemented: POST /api/predict.
- [x] Health endpoint implemented: GET /api/health.
- [x] Recommendation engine implemented in backend/src/services/recommendation.py.
- [x] Angular integration files scaffolded for prediction form and result display.
- [ ] Connect Angular components into app.module.ts and app.component.ts after Angular project bootstrap.
- [ ] End-to-end test frontend to backend request flow.

## Immediate Next Steps

1. Download the Kaggle CSV and place it at data/retail_sales_dataset.csv.
2. Setup Python environment and install backend/requirements.txt.
3. Run training and verify metrics.json is generated in models/.
4. Start FastAPI and test /api/predict with a sample payload.
5. Bootstrap Angular app (if not initialized) and wire the provided components and service.
6. Run a short demo scenario and document whether recommendations are useful for decision-making.

## Success Criteria

- Model produces stable MAE and RMSE on held-out time-based test data.
- Prototype returns prediction + recommendation for valid product/date input.
- Final report includes evidence of how predictions can guide stock decisions.
## Plan: Small-Business Sales AI Prototype

Build an end-to-end MVP that proves whether a simple AI model can improve small-business decisions by predicting next-day product sales, then translating predictions into clear stock actions. The approach prioritizes simplicity and explainability: robust preprocessing, baseline Linear Regression, Random Forest comparison, and a minimal FastAPI + Angular decision-support app.

**Steps**
1. Phase 1 - Project setup and data intake: create backend/frontend/data/models structure, define environment dependencies, download and place the Kaggle dataset, and document dataset version and expected schema in the project README. This step unblocks all later work.
2. Phase 2 - Data understanding and quality checks: perform EDA to confirm available fields, target definition, data volume by product/date, and data issues (missing values, invalid prices/quantities, duplicates, outliers). Output: a short EDA summary that locks assumptions for preprocessing. Depends on step 1.
3. Phase 3 - Preprocessing pipeline: implement reusable preprocessing for missing-value handling, date parsing, and feature engineering (day-of-week, month, weekend, optionally lag features if historical continuity allows). Apply categorical encoding and scaling only where required by model type. Persist fitted transformers for consistent inference. Depends on step 2.
4. Phase 4 - Temporal split and baseline training: define a time-based train/validation/test split to prevent leakage, train Linear Regression as baseline, evaluate MAE and RMSE on validation and test sets, and save metrics/artifacts. Depends on step 3.
5. Phase 5 - Random Forest comparison in MVP: train Random Forest Regressor with a constrained hyperparameter search, evaluate on the same split and metrics, and compare against baseline. Keep the simplest acceptable model as default deployment model (best MAE/RMSE with reasonable training time). Depends on step 4.
6. Phase 6 - Decision rule layer: define deterministic recommendation rules mapping predicted demand to actions (Increase stock, Maintain stock, Reduce inventory) based on thresholds tied to recent average demand and configurable safety margins. Depends on step 4 and step 5.
7. Phase 7 - Backend API (FastAPI): expose endpoints for health, prediction, and optional retrain/metrics retrieval; validate inputs (product/date), run preprocessing + model inference, and return prediction plus recommendation text. Depends on step 6.
8. Phase 8 - Angular prototype UI: build a single-page flow with product/date input, prediction result card, recommendation message, and basic error/loading states. Integrate with backend API service and handle validation feedback. Depends on step 7.
9. Phase 9 - End-to-end verification and demo narrative: run API + UI integration tests, sanity-check predictions on known historical cases, and prepare a short evidence summary that answers the research question using model metrics and example business decisions. Depends on step 8.
10. Parallelizable work notes: while step 3-5 are in progress, frontend shell scaffolding can start in parallel; final UI wiring still depends on step 7 API contract.

**Relevant files**
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/plan.md - canonical project plan for handoff and execution tracking.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/backend/src/data/preprocessing.py - missing value logic, datetime parsing, feature creation, encoding/scaling pipeline.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/backend/src/models/trainer.py - model training orchestration for Linear Regression and Random Forest.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/backend/src/models/evaluator.py - MAE/RMSE calculation and model comparison summary.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/backend/src/models/artifacts.py - save/load model and preprocessors.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/backend/src/api/app.py - FastAPI app bootstrap and router registration.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/backend/src/api/routes/predict.py - prediction endpoint contract and response payload.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/backend/src/services/recommendation.py - threshold-based stock recommendation rules.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/frontend/src/app/services/api.service.ts - Angular HTTP service for prediction requests.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/frontend/src/app/components/predict/predict.component.ts - input form and submit flow.
- c:/Users/bnnuyen/NHI_UYEN/projects/sale-prediction/frontend/src/app/components/result/result.component.ts - predicted sales and recommendation display.

**Verification**
1. Data checks: verify no nulls remain in required model features and datetime-derived columns are valid across the full dataset.
2. Leakage checks: confirm all training rows occur strictly before validation/test rows.
3. Metric checks: report MAE and RMSE for both models on identical test data and identify selected default model.
4. API checks: test valid/invalid payloads and ensure response includes predicted_sales, recommendation, and confidence/context fields if defined.
5. UI checks: manually test desktop and mobile form flow, error states, and successful prediction rendering.
6. End-to-end checks: run one realistic scenario (selected product/date) and confirm recommendation aligns with configured thresholds.

**Decisions**
- Backend framework: FastAPI.
- Forecast target: next-day sales per product.
- Model scope: Linear Regression and Random Forest both included in MVP comparison.
- Included scope: one prediction workflow, two regression models, MAE/RMSE evaluation, and a simple decision-support recommendation.
- Excluded for now: deep learning models, advanced MLOps/deployment automation, multi-location optimization, and fully automated retraining pipeline.

**Further Considerations**
1. Recommendation threshold policy: choose either fixed global thresholds for simplicity or product-specific thresholds for better realism.
2. Data granularity decision: product-only versus product + store if store/location exists in dataset.
3. Explainability option: include top contributing features from Random Forest permutation importance as an optional insight panel.