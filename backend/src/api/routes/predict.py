from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from sklearn.metrics import mean_absolute_percentage_error

from src.api.schemas import (
    AccuracyTrendPoint,
    EvaluationResponse,
    EvaluationRow,
    EvaluationSummary,
    ForecastDayRow,
    ForecastRangeRequest,
    ForecastRangeResponse,
    ForecastSummary,
    PredictRequest,
    PredictResponse,
    ProductComparisonMetric,
    ProductComparisonResponse,
)
from src.config import CHARTS_DIR, DEFAULT_DATASET, METRICS_PATH, MODEL_PATH
from src.data.preprocessing import DataValidationError, build_inference_row, prepare_training_data
from src.models.artifacts import load_metrics, load_model
from src.services.recommendation import stock_suggestion

router = APIRouter(tags=["prediction"])
_EVALUATION_CACHE: dict[str, Any] = {"signature": None, "response": None}


def _get_file_mtime(path: Path) -> float:
    if not path.exists():
        return 0.0
    return path.stat().st_mtime


def _evaluation_signature() -> tuple[float, float]:
    return (_get_file_mtime(MODEL_PATH), _get_file_mtime(DEFAULT_DATASET))


def _save_evaluation_chart(actual: np.ndarray, predictions: np.ndarray) -> tuple[str, str]:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    chart_filename = "model_evaluation.png"
    chart_path = CHARTS_DIR / chart_filename
    sample_size = min(200, len(actual), len(predictions))

    x_values = list(range(1, sample_size + 1))
    actual_sample = actual[:sample_size]
    prediction_sample = predictions[:sample_size]

    plt.figure(figsize=(12, 6))
    plt.plot(x_values, actual_sample, label="Actual Sales", linewidth=2)
    plt.plot(x_values, prediction_sample, label="Predicted Sales", linewidth=2)
    plt.title("Model Evaluation: Actual vs Predicted")
    plt.xlabel("Sample Index")
    plt.ylabel("Sales")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()

    return f"/static/charts/{chart_filename}", str(chart_path)


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    model = load_model(MODEL_PATH)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run training first.")

    try:
        feature_row = build_inference_row(
            payload.product,
            payload.date,
            payload.recent_average_sales,
        )
    except DataValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    prediction = float(model.predict(feature_row)[0])
    metrics = load_metrics(METRICS_PATH)

    return PredictResponse(
        product=payload.product,
        date=payload.date,
        predicted_sales=round(prediction, 2),
        suggestion=stock_suggestion(prediction, payload.recent_average_sales),
        selected_model=metrics.get("selected_model"),
    )


@router.post("/forecast-range", response_model=ForecastRangeResponse)
def forecast_range(payload: ForecastRangeRequest) -> ForecastRangeResponse:
    model = load_model(MODEL_PATH)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run training first.")

    try:
        start_date = datetime.strptime(payload.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(payload.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.") from None

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date.") from None

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    if len(date_range) > 90:
        raise HTTPException(status_code=400, detail="Date range limited to 90 days maximum.") from None

    daily_rows = []
    increase_count = 0
    reduce_count = 0
    maintain_count = 0
    total_sales = 0.0

    for current_date in date_range:
        date_str = current_date.strftime("%Y-%m-%d")
        try:
            feature_row = build_inference_row(
                payload.product,
                date_str,
                payload.recent_average_sales,
            )
            prediction = float(model.predict(feature_row)[0])
            suggestion = stock_suggestion(prediction, payload.recent_average_sales)

            daily_rows.append(
                ForecastDayRow(
                    date=date_str,
                    predicted_sales=round(prediction, 2),
                    suggestion=suggestion,
                )
            )
            total_sales += prediction

            if suggestion == "Increase stock":
                increase_count += 1
            elif suggestion == "Reduce inventory":
                reduce_count += 1
            else:
                maintain_count += 1
        except (DataValidationError, ValueError):
            continue

    if not daily_rows:
        raise HTTPException(status_code=400, detail="No valid predictions generated for the date range.") from None

    metrics = load_metrics(METRICS_PATH)
    avg_sales = total_sales / len(daily_rows) if daily_rows else 0.0

    return ForecastRangeResponse(
        daily_rows=daily_rows,
        summary=ForecastSummary(
            total_days=len(daily_rows),
            avg_predicted_sales=round(avg_sales, 2),
            increase_stock_count=increase_count,
            reduce_inventory_count=reduce_count,
            maintain_stock_count=maintain_count,
        ),
        selected_model=metrics.get("selected_model"),
    )


@router.get("/model-evaluation", response_model=EvaluationResponse)
def model_evaluation() -> EvaluationResponse:
    signature = _evaluation_signature()
    cached_signature = _EVALUATION_CACHE.get("signature")
    cached_response = _EVALUATION_CACHE.get("response")
    if cached_signature == signature and isinstance(cached_response, EvaluationResponse):
        return cached_response

    model = load_model(MODEL_PATH)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run training first.")

    try:
        raw_df = pd.read_csv(DEFAULT_DATASET)
        training_data = prepare_training_data(raw_df)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(exc)}") from exc

    predictions = np.asarray(model.predict(training_data.X), dtype=float)
    actual = np.asarray(training_data.y.values, dtype=float)

    absolute_errors = np.abs(actual - predictions)
    with np.errstate(divide="ignore", invalid="ignore"):
        error_percentages = np.where(actual != 0, (absolute_errors / np.abs(actual)) * 100, 0.0)

    mae = float(absolute_errors.mean()) if absolute_errors.size else 0.0
    rmse_val = float(np.sqrt(np.mean((actual - predictions) ** 2))) if absolute_errors.size else 0.0
    mape = float(mean_absolute_percentage_error(actual, predictions)) if absolute_errors.size else 0.0

    evaluation_rows = []
    for i in range(min(100, len(predictions))):
        date_str = (
            training_data.dates.iloc[i].strftime("%Y-%m-%d")
            if hasattr(training_data.dates.iloc[i], "strftime")
            else str(training_data.dates.iloc[i])
        )
        evaluation_rows.append(
            EvaluationRow(
                date=date_str,
                product="mixed",
                actual_sales=round(float(actual[i]), 2),
                predicted_sales=round(float(predictions[i]), 2),
                absolute_error=round(float(absolute_errors[i]), 2),
                error_percentage=round(float(error_percentages[i]), 2),
            )
        )

    metrics = load_metrics(METRICS_PATH)
    accuracy_trend = [
        AccuracyTrendPoint(
            period="Overall",
            mae=round(mae, 2),
            rmse=round(rmse_val, 2),
            mape=round(mape, 2),
        )
    ]

    best_product = "Linear Regression"
    worst_product = "Random Forest"
    if metrics:
        best_product = metrics.get("selected_model", "Linear Regression")

    try:
        chart_image_url, chart_image_path = _save_evaluation_chart(actual, predictions)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating evaluation chart: {str(exc)}") from exc

    response = EvaluationResponse(
        evaluation_rows=evaluation_rows,
        summary=EvaluationSummary(
            total_samples=len(predictions),
            overall_mae=round(mae, 2),
            overall_rmse=round(rmse_val, 2),
            overall_mape=round(mape, 2),
            best_product=best_product,
            worst_product=worst_product,
        ),
        accuracy_trend=accuracy_trend,
        chart_image_url=chart_image_url,
        chart_image_path=chart_image_path,
    )

    _EVALUATION_CACHE["signature"] = signature
    _EVALUATION_CACHE["response"] = response
    return response


@router.post("/compare-products", response_model=ProductComparisonResponse)
def compare_products(products: list[str]) -> ProductComparisonResponse:
    model = load_model(MODEL_PATH)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run training first.")

    comparison_metrics = []
    highest_avg = 0.0
    highest_product = products[0] if products else "Unknown"

    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)

    for product in products:
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        daily_predictions = []
        increase_count = 0
        reduce_count = 0
        maintain_count = 0

        for current_date in date_range:
            date_str = current_date.strftime("%Y-%m-%d")
            try:
                feature_row = build_inference_row(product, date_str)
                prediction = float(model.predict(feature_row)[0])
                daily_predictions.append(prediction)
                suggestion = stock_suggestion(prediction)

                if suggestion == "Increase stock":
                    increase_count += 1
                elif suggestion == "Reduce inventory":
                    reduce_count += 1
                else:
                    maintain_count += 1
            except DataValidationError:
                continue

        if daily_predictions:
            avg_sales = sum(daily_predictions) / len(daily_predictions)
            total_sales = sum(daily_predictions)

            if avg_sales > highest_avg:
                highest_avg = avg_sales
                highest_product = product

            comparison_metrics.append(
                ProductComparisonMetric(
                    product=product,
                    total_days=len(daily_predictions),
                    avg_predicted_sales=round(avg_sales, 2),
                    sum_predicted_sales=round(total_sales, 2),
                    increase_stock_count=increase_count,
                    reduce_inventory_count=reduce_count,
                    maintain_stock_count=maintain_count,
                )
            )

    metrics = load_metrics(METRICS_PATH)

    return ProductComparisonResponse(
        comparison_metrics=comparison_metrics,
        highest_demand_product=highest_product,
        highest_demand_average_sales=round(highest_avg, 2),
        selected_model=metrics.get("selected_model"),
    )


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
