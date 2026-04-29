from __future__ import annotations

import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from sklearn.metrics import r2_score

from src.api.schemas import (
    ModelEvaluationResponse,
    OverfittingAnalysis,
)
from src.config import CHARTS_DIR, MODEL_PATH
from src.data.preprocessing import prepare_training_data
from src.models.artifacts import load_model

router = APIRouter(tags=["model-evaluation"])


def _save_uploaded_evaluation_chart(
    actual: np.ndarray,
    predictions: np.ndarray,
    file_name: str,
) -> tuple[str, str]:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    stem = Path(file_name or "uploaded_dataset").stem
    safe_stem = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in stem)
    chart_filename = f"model_evaluation_{safe_stem}.png"
    chart_path = CHARTS_DIR / chart_filename

    sample_size = min(200, len(actual), len(predictions))
    x_values = list(range(1, sample_size + 1))
    actual_sample = actual[:sample_size]
    prediction_sample = predictions[:sample_size]

    plt.figure(figsize=(12, 6))
    plt.plot(x_values, actual_sample, label="Actual Sales", linewidth=2)
    plt.plot(x_values, prediction_sample, label="Predicted Sales", linewidth=2)
    plt.title("Model Evaluation (Uploaded CSV): Actual vs Predicted")
    plt.xlabel("Sample Index")
    plt.ylabel("Sales")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()

    return f"/static/charts/{chart_filename}", str(chart_path)


@router.post("/model-evaluation/csv", response_model=ModelEvaluationResponse)
async def evaluate_with_csv(
    file: UploadFile = File(..., description="CSV file with columns matching training data"),
) -> ModelEvaluationResponse:
    """
    Evaluate the trained model on a user-provided CSV dataset.
    
    The CSV file should have the same columns as the training dataset:
    - Date, Customer ID, Gender, Age, Product Category, Quantity, Price per Unit, Total Amount
    
    Returns comprehensive evaluation metrics including:
    - MAE, RMSE, R², MAPE
    - Overfitting analysis (comparison with training data if available)
    - Error distribution statistics
    """
    
    # Load trained model
    model = load_model(MODEL_PATH)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run training first.")
    
    # Validate and read CSV file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file (.csv)")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read CSV file: {str(exc)}"
        ) from exc
    
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    
    # Prepare data for evaluation
    try:
        prepared_data = prepare_training_data(df)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to prepare data: {str(exc)}. "
                   "Ensure CSV has required columns: Date, Customer ID, Gender, Age, "
                   "Product Category, Quantity, Price per Unit, Total Amount"
        ) from exc
    
    X = prepared_data.X.reset_index(drop=True)
    y = prepared_data.y.reset_index(drop=True)
    
    if len(X) == 0:
        raise HTTPException(status_code=400, detail="No valid records to evaluate")
    
    # Make predictions
    try:
        y_pred = model.predict(X)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model prediction failed: {str(exc)}"
        ) from exc
    
    # Calculate metrics
    y_true = np.asarray(y.values, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    mae = float(np.mean(np.abs(y_true - y_pred)))
    mse = float(np.mean((y_true - y_pred) ** 2))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    
    # Calculate MAPE safely
    with np.errstate(divide="ignore", invalid="ignore"):
        mape = float(np.mean(np.abs((y_true - y_pred) / y_true))) * 100
        if np.isnan(mape) or np.isinf(mape):
            mape = 0.0
    
    # Error distribution
    absolute_errors = np.abs(y_true - y_pred)
    error_percentages = np.where(y_true != 0, (absolute_errors / y_true) * 100, 0.0)
    
    # Analyze overfitting (compare with training performance if typical)
    overfitting_analysis = OverfittingAnalysis(
        mae=round(mae, 4),
        rmse=round(rmse, 4),
        r2=round(r2, 4),
        mape=round(mape, 2),
        is_acceptable=r2 > 0.8,
        interpretation="High R² indicates good generalization" if r2 > 0.9 else (
            "R² is acceptable" if r2 > 0.8 else "R² suggests poor model fit"
        )
    )
    
    # Error distribution statistics
    error_stats = {
        "mean_error": round(float(absolute_errors.mean()), 2),
        "median_error": round(float(np.median(absolute_errors)), 2),
        "std_error": round(float(absolute_errors.std()), 2),
        "max_error": round(float(absolute_errors.max()), 2),
        "min_error": round(float(absolute_errors.min()), 2),
        "predictions_within_10_percent": int(np.sum(error_percentages < 10)),
        "predictions_within_20_percent": int(np.sum(error_percentages < 20)),
        "predictions_within_30_percent": int(np.sum(error_percentages < 30)),
    }
    
    # Sample predictions (first 50 rows)
    sample_predictions = []
    for i in range(min(50, len(y_true))):
        sample_predictions.append({
            "actual": round(float(y_true[i]), 2),
            "predicted": round(float(y_pred[i]), 2),
            "absolute_error": round(float(absolute_errors[i]), 2),
            "error_percentage": round(float(error_percentages[i]), 2),
        })

    try:
        chart_image_url, chart_image_path = _save_uploaded_evaluation_chart(
            y_true,
            y_pred,
            file.filename or "uploaded_dataset.csv",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate evaluation chart: {str(exc)}",
        ) from exc
    
    return ModelEvaluationResponse(
        dataset_name=file.filename,
        total_samples=int(len(y_true)),
        metrics=overfitting_analysis,
        error_statistics=error_stats,
        sample_predictions=sample_predictions,
        chart_image_url=chart_image_url,
        chart_image_path=chart_image_path,
        file_uploaded_successfully=True,
    )
