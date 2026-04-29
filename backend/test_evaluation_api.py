#!/usr/bin/env python3
"""
Test script for the Model Evaluation API endpoint.

Usage:
    python test_evaluation_api.py
    python test_evaluation_api.py --url http://localhost:8000
    python test_evaluation_api.py --file ../data/retail_sales_dataset_test.csv
"""

import argparse
import json
import sys
from pathlib import Path

import requests


def test_evaluation_api(api_url: str, csv_file: str) -> None:
    """Test the model evaluation API with a CSV file."""
    
    # Verify file exists
    file_path = Path(csv_file)
    if not file_path.exists():
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)
    
    if not file_path.suffix.lower() == ".csv":
        print(f"❌ Error: File must be CSV: {csv_file}")
        sys.exit(1)
    
    print(f"📤 Uploading file: {file_path.name}")
    print(f"📍 API URL: {api_url}/api/model-evaluation/csv")
    print()
    
    try:
        # Upload file
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{api_url}/api/model-evaluation/csv",
                files=files,
                timeout=60
            )
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            print_results(result)
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.json())
            sys.exit(1)
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Cannot reach {api_url}")
        print("   Make sure the API server is running:")
        print("   cd backend && python -m uvicorn src.api.app:app --reload")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long")
        sys.exit(1)
    except Exception as exc:
        print(f"❌ Error: {str(exc)}")
        sys.exit(1)


def print_results(result: dict) -> None:
    """Print evaluation results in a readable format."""
    
    print("=" * 80)
    print("🎯 MODEL EVALUATION RESULTS")
    print("=" * 80)
    
    # Dataset info
    print(f"\n📊 Dataset: {result['dataset_name']}")
    print(f"   Total Samples: {result['total_samples']:,}")
    if result.get("chart_image_url"):
        print(f"   Chart URL: {result['chart_image_url']}")
    if result.get("chart_image_path"):
        print(f"   Chart Path: {result['chart_image_path']}")
    
    # Metrics
    metrics = result["metrics"]
    print(f"\n📈 Performance Metrics:")
    print(f"   MAE (Mean Absolute Error):     {metrics['mae']:,.2f}")
    print(f"   RMSE (Root Mean Squared Error): {metrics['rmse']:,.2f}")
    print(f"   R² (Coefficient of Determination): {metrics['r2']:.4f}")
    print(f"   MAPE (Mean Absolute % Error):  {metrics['mape']:.2f}%")
    
    # Interpretation
    status_emoji = "✅" if metrics["is_acceptable"] else "⚠️"
    print(f"\n{status_emoji} Status: {metrics['interpretation']}")
    print(f"   Acceptable: {'Yes' if metrics['is_acceptable'] else 'No'}")
    
    # Error statistics
    errors = result["error_statistics"]
    print(f"\n📊 Error Distribution:")
    print(f"   Mean Error:    {errors['mean_error']:,.2f}")
    print(f"   Median Error:  {errors['median_error']:,.2f}")
    print(f"   Std Deviation: {errors['std_error']:,.2f}")
    print(f"   Min Error:     {errors['min_error']:,.2f}")
    print(f"   Max Error:     {errors['max_error']:,.2f}")
    
    # Accuracy buckets
    total = result['total_samples']
    print(f"\n🎯 Prediction Accuracy:")
    within_10 = errors['predictions_within_10_percent']
    within_20 = errors['predictions_within_20_percent']
    within_30 = errors['predictions_within_30_percent']
    
    print(f"   Within 10%: {within_10:,} / {total:,} ({within_10/total*100:.1f}%)")
    print(f"   Within 20%: {within_20:,} / {total:,} ({within_20/total*100:.1f}%)")
    print(f"   Within 30%: {within_30:,} / {total:,} ({within_30/total*100:.1f}%)")
    
    # Sample predictions
    samples = result["sample_predictions"]
    print(f"\n📋 Sample Predictions (First {len(samples)} rows):")
    print("-" * 80)
    print(f"{'Actual':<12} {'Predicted':<12} {'Error':<12} {'Error %':<10}")
    print("-" * 80)
    
    for pred in samples[:10]:  # Show first 10
        actual = pred["actual"]
        predicted = pred["predicted"]
        error = pred["absolute_error"]
        error_pct = pred["error_percentage"]
        print(f"{actual:>11.2f} {predicted:>11.2f} {error:>11.2f} {error_pct:>9.2f}%")
    
    if len(samples) > 10:
        print(f"... and {len(samples) - 10} more samples")
    
    print("\n" + "=" * 80)
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if metrics["r2"] > 0.9:
        print("   ✅ Excellent model performance! Ready for production.")
    elif metrics["r2"] > 0.8:
        print("   ✅ Good model performance. Suitable for most use cases.")
    elif metrics["r2"] > 0.7:
        print("   ⚠️  Acceptable performance. Consider improvements.")
    else:
        print("   ❌ Poor performance. Model needs retraining or adjustment.")
    
    if metrics["mape"] < 5:
        print("   ✅ Excellent accuracy (MAPE < 5%)")
    elif metrics["mape"] < 10:
        print("   ✅ Good accuracy (MAPE < 10%)")
    elif metrics["mape"] < 20:
        print("   ⚠️  Acceptable accuracy (MAPE < 20%)")
    else:
        print("   ❌ Poor accuracy (MAPE > 20%)")
    
    print("\n" + "=" * 80)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test the Model Evaluation API endpoint"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="../data/retail_sales_dataset_test.csv",
        help="CSV file to evaluate (default: ../data/retail_sales_dataset_test.csv)"
    )
    
    args = parser.parse_args()
    test_evaluation_api(args.url, args.file)


if __name__ == "__main__":
    main()
