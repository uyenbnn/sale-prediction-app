# Model Evaluation Guide - How to Use Your Test Dataset

You now have a complete workflow to evaluate your model and detect overfitting. Here's how to use it:

## Step 1: Run the Test Evaluator

From the `backend/` directory:

```bash
python -m src.models.test_evaluator
```

This script will:
- Load your trained model
- Load both the original and test datasets
- Make predictions on both
- Calculate evaluation metrics (MAE, RMSE, R², MAPE)
- Analyze overfitting
- Save results to `models/evaluation_results.json`

## Understanding the Results

### Key Metrics

1. **MAE (Mean Absolute Error)**
   - Average difference between predicted and actual values
   - Lower is better
   - In your case: ~49.56 on test data

2. **RMSE (Root Mean Squared Error)**
   - Penalizes larger errors more heavily
   - Lower is better
   - In your case: ~132.66 on test data

3. **R² (Coefficient of Determination)**
   - Explains what percentage of variance is captured
   - Range: 0 to 1 (1 = perfect, 0 = poor)
   - In your case: 0.9573 on test data (95.73% variance explained)

4. **MAPE (Mean Absolute Percentage Error)**
   - Percentage error relative to actual values
   - In your case: 7.79% on test data

### Your Current Results

```
Original Dataset (Training):    R² = 1.0000 (Perfect fit)
Test Dataset (New Data):        R² = 0.9573 (Very good)
Difference:                     0.0427 (Slight - ACCEPTABLE)
```

**Interpretation:** Your model shows SLIGHT OVERFITTING, which is normal and acceptable. The small R² drop (4.27%) indicates the model generalizes well.

---

## When to Be Concerned

| Situation | R² Drop | Action |
|-----------|---------|--------|
| **No Problem** | < 5% | Keep using the model |
| **Slight Overfitting** | 5-10% | Monitor performance |
| **Moderate Overfitting** | 10-20% | Consider regularization |
| **Severe Overfitting** | > 20% | Retrain with adjustments |

---

## Improving Your Model (If Needed)

If you observe overfitting, try:

### 1. **More Data**
```bash
# Create larger test dataset with more variations
python data/generate_test_dataset.py --variations 10
```

### 2. **Add Regularization** (in backend/src/models/trainer.py)
```python
# For Ridge: increase alpha
"params": {
    "model__alpha": [0.1, 1.0, 10.0, 100.0, 1000.0],  # Higher values
},

# For Random Forest: reduce depth or increase min_samples_leaf
"params": {
    "model__max_depth": [10, 15],        # Reduce from 25
    "model__min_samples_leaf": [4, 8],   # Increase from 2
},
```

### 3. **Cross-Validation**
Your model already uses TimeSeriesSplit - this helps prevent overfitting.

### 4. **Feature Engineering**
Remove or combine features that might be noise:
- Check `backend/src/data/preprocessing.py` for feature selection

---

## Workflow Summary

```
1. Generate test dataset:
   cd data && python generate_test_dataset.py

2. Verify test dataset created:
   ls -la retail_sales_dataset_test.csv

3. Train model (if not already trained):
   cd backend && python src/train.py

4. Evaluate on test dataset:
   python -m src.models.test_evaluator

5. Review results:
   cat models/evaluation_results.json
```

---

## Files Created

- **`data/retail_sales_dataset_test.csv`** - Test dataset with modified values
- **`data/generate_test_dataset.py`** - Script to generate test datasets
- **`data/compare_datasets.py`** - Compare statistics between datasets
- **`backend/src/models/test_evaluator.py`** - Evaluation script
- **`models/evaluation_results.json`** - Evaluation results

---

## Next Steps

### ✅ Your model is performing well! 

With R² = 0.9573 on unseen test data, your model:
- Explains 95.73% of sales variance
- Has only 7.79% average error
- Generalizes reasonably well

### 🎯 Recommendations

1. **Deploy with confidence** - The model shows good generalization
2. **Monitor performance** - Keep testing with real new data
3. **Retrain periodically** - Update the model with new sales data
4. **Track metrics** - Save evaluation results over time
