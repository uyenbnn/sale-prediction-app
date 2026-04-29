from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.config import MODEL_PATH, METRICS_PATH, DATA_DIR
from src.data.preprocessing import prepare_training_data
from src.models.artifacts import load_model, load_metrics


def evaluate_on_test_dataset() -> None:
    """
    Evaluate the trained model on a new test dataset to detect overfitting.
    
    This compares the model's performance on:
    - Original training data
    - New test dataset with modified values
    """
    
    # Load paths
    test_dataset_path = DATA_DIR / "retail_sales_dataset_test.csv"
    original_dataset_path = DATA_DIR / "retail_sales_dataset.csv"
    
    if not test_dataset_path.exists():
        print("❌ Test dataset not found. Run generate_test_dataset.py first.")
        return
    
    if not MODEL_PATH.exists():
        print("❌ Model not found. Train the model first with: python src/train.py")
        return
    
    # Load the trained model
    print("[Loading] Trained model...")
    model = load_model(MODEL_PATH)
    if model is None:
        print("❌ Failed to load model")
        return
    
    # Load training metrics
    training_metrics = load_metrics(METRICS_PATH)
    print(f"[OK] Model loaded: {MODEL_PATH}")
    
    # Load datasets
    print("[Loading] Datasets...")
    original_df = pd.read_csv(original_dataset_path)
    test_df = pd.read_csv(test_dataset_path)
    print(f"  Original dataset: {len(original_df)} rows")
    print(f"  Test dataset: {len(test_df)} rows")
    
    # Prepare data for evaluation
    print("\n[Preparing] Data preprocessing...")
    
    # Prepare original data (training data)
    original_prepared = prepare_training_data(original_df)
    X_original = original_prepared.X.reset_index(drop=True)
    y_original = original_prepared.y.reset_index(drop=True)
    
    # Prepare test data
    test_prepared = prepare_training_data(test_df)
    X_test = test_prepared.X.reset_index(drop=True)
    y_test = test_prepared.y.reset_index(drop=True)
    
    # Make predictions
    print("[Predicting] Original dataset...")
    y_pred_original = model.predict(X_original)
    
    print("[Predicting] Test dataset...")
    y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    mae_original = mean_absolute_error(y_original, y_pred_original)
    rmse_original = np.sqrt(mean_squared_error(y_original, y_pred_original))
    r2_original = r2_score(y_original, y_pred_original)
    mape_original = np.mean(np.abs((y_original - y_pred_original) / y_original)) * 100
    
    mae_test = mean_absolute_error(y_test, y_pred_test)
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2_test = r2_score(y_test, y_pred_test)
    mape_test = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
    
    # Calculate overfitting indicators
    mae_diff = mae_test - mae_original
    rmse_diff = rmse_test - rmse_original
    r2_diff = r2_original - r2_test
    
    # Print results
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    
    print("\n📊 ORIGINAL DATASET (Training Data):")
    print(f"  MAE:    {mae_original:,.2f}")
    print(f"  RMSE:   {rmse_original:,.2f}")
    print(f"  R²:     {r2_original:.4f}")
    print(f"  MAPE:   {mape_original:.2f}%")
    
    print("\n📊 TEST DATASET (New Data with Modified Values):")
    print(f"  MAE:    {mae_test:,.2f}")
    print(f"  RMSE:   {rmse_test:,.2f}")
    print(f"  R²:     {r2_test:.4f}")
    print(f"  MAPE:   {mape_test:.2f}%")
    
    print("\n📈 DIFFERENCES (Test - Original):")
    if mae_original > 0:
        mae_pct = mae_diff/mae_original*100
        print(f"  MAE Δ:  {mae_diff:+,.2f} ({mae_pct:+.2f}%)")
    else:
        print(f"  MAE Δ:  {mae_diff:+,.2f} (N/A - original MAE was 0)")
    
    if rmse_original > 0:
        rmse_pct = rmse_diff/rmse_original*100
        print(f"  RMSE Δ: {rmse_diff:+,.2f} ({rmse_pct:+.2f}%)")
    else:
        print(f"  RMSE Δ: {rmse_diff:+,.2f} (N/A - original RMSE was 0)")
    
    print(f"  R² Δ:   {r2_diff:+.4f}")
    
    print("\n" + "="*80)
    print("OVERFITTING ANALYSIS")
    print("="*80)
    
    if r2_diff > 0.1:
        print("⚠️  CRITICAL OVERFITTING DETECTED!")
        print(f"   R² drop of {r2_diff:.4f} indicates severe overfitting.")
    elif r2_diff > 0.05:
        print("⚠️  MODERATE OVERFITTING DETECTED")
        print(f"   R² drop of {r2_diff:.4f} indicates some overfitting.")
    elif r2_diff > 0:
        print("ℹ️  SLIGHT OVERFITTING (normal)")
        print(f"   Minor R² drop of {r2_diff:.4f} is acceptable.")
    else:
        print("✓  NO OVERFITTING DETECTED")
        print("   Model generalizes well! Performance improved on test data.")
    
    if mae_original > 0 and mae_diff > mae_original * 0.1:
        mae_pct = mae_diff/mae_original*100
        print(f"⚠️  MAE increased by {mae_pct:.2f}% on test data.")
    elif mae_original > 0:
        mae_pct = mae_diff/mae_original*100
        print(f"✓  MAE stable (±{mae_pct:.2f}%)")
    else:
        print(f"⚠️  Original MAE was 0 (perfect fit - likely overfitting)")
        print(f"    Test MAE: {mae_test:,.2f} - This is expected generalization error")
    
    # Save evaluation results
    results = {
        "original_dataset": {
            "mae": round(float(mae_original), 4),
            "rmse": round(float(rmse_original), 4),
            "r2": round(float(r2_original), 4),
            "mape": round(float(mape_original), 2),
        },
        "test_dataset": {
            "mae": round(float(mae_test), 4),
            "rmse": round(float(rmse_test), 4),
            "r2": round(float(r2_test), 4),
            "mape": round(float(mape_test), 2),
        },
        "differences": {
            "mae_delta": round(float(mae_diff), 4),
            "rmse_delta": round(float(rmse_diff), 4),
            "r2_delta": round(float(r2_diff), 4),
            "mae_delta_percent": round(float(mae_diff/mae_original*100), 2) if mae_original > 0 else None,
            "rmse_delta_percent": round(float(rmse_diff/rmse_original*100), 2) if rmse_original > 0 else None,
        },
    }
    
    eval_path = Path(__file__).resolve().parents[2] / "models" / "evaluation_results.json"
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n💾 Results saved to: {eval_path}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    evaluate_on_test_dataset()
