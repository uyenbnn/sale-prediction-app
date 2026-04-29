from __future__ import annotations

import pandas as pd
import numpy as np

from src.config import MODEL_PATH, DATA_DIR
from src.data.preprocessing import prepare_training_data
from src.models.artifacts import load_model


def visualize_predictions() -> None:
    """
    Show side-by-side predictions on original and test datasets.
    """
    
    test_dataset_path = DATA_DIR / "retail_sales_dataset_test.csv"
    original_dataset_path = DATA_DIR / "retail_sales_dataset.csv"
    
    if not MODEL_PATH.exists():
        print("❌ Model not found. Train the model first.")
        return
    
    # Load model and datasets
    model = load_model(MODEL_PATH)
    original_df = pd.read_csv(original_dataset_path)
    test_df = pd.read_csv(test_dataset_path)
    
    # Prepare data
    original_prepared = prepare_training_data(original_df)
    X_original = original_prepared.X.reset_index(drop=True)
    y_original = original_prepared.y.reset_index(drop=True)
    
    test_prepared = prepare_training_data(test_df)
    X_test = test_prepared.X.reset_index(drop=True)
    y_test = test_prepared.y.reset_index(drop=True)
    
    # Make predictions
    y_pred_original = model.predict(X_original)
    y_pred_test = model.predict(X_test)
    
    # Calculate errors
    errors_original = np.abs(y_original - y_pred_original)
    errors_test = np.abs(y_test - y_pred_test)
    
    print("\n" + "="*100)
    print("PREDICTION COMPARISON - FIRST 20 ROWS")
    print("="*100)
    
    print("\n🏋️  ORIGINAL DATASET (Training Data):")
    print("-" * 100)
    print(f"{'Row':<4} {'Actual':<12} {'Predicted':<12} {'Error':<12} {'Error %':<10}")
    print("-" * 100)
    
    for i in range(min(20, len(y_original))):
        actual = y_original.iloc[i]
        pred = y_pred_original[i]
        error = errors_original[i]
        pct = (error / actual * 100) if actual != 0 else 0
        print(f"{i+1:<4} {actual:>11.2f} {pred:>11.2f} {error:>11.2f} {pct:>9.2f}%")
    
    print("\n📊 TEST DATASET (New Data):")
    print("-" * 100)
    print(f"{'Row':<4} {'Actual':<12} {'Predicted':<12} {'Error':<12} {'Error %':<10}")
    print("-" * 100)
    
    for i in range(min(20, len(y_test))):
        actual = y_test.iloc[i]
        pred = y_pred_test[i]
        error = errors_test[i]
        pct = (error / actual * 100) if actual != 0 else 0
        print(f"{i+1:<4} {actual:>11.2f} {pred:>11.2f} {error:>11.2f} {pct:>9.2f}%")
    
    print("\n" + "="*100)
    print("ERROR DISTRIBUTION ANALYSIS")
    print("="*100)
    
    print("\n📈 Original Dataset Errors:")
    print(f"  Mean Error:     {errors_original.mean():.2f}")
    print(f"  Median Error:   {np.median(errors_original):.2f}")
    print(f"  Std Dev:        {errors_original.std():.2f}")
    print(f"  Max Error:      {errors_original.max():.2f}")
    print(f"  Min Error:      {errors_original.min():.2f}")
    print(f"  Errors < 100:   {sum(errors_original < 100)} / {len(errors_original)}")
    
    print("\n📈 Test Dataset Errors:")
    print(f"  Mean Error:     {errors_test.mean():.2f}")
    print(f"  Median Error:   {np.median(errors_test):.2f}")
    print(f"  Std Dev:        {errors_test.std():.2f}")
    print(f"  Max Error:      {errors_test.max():.2f}")
    print(f"  Min Error:      {errors_test.min():.2f}")
    print(f"  Errors < 100:   {sum(errors_test < 100)} / {len(errors_test)}")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    visualize_predictions()
