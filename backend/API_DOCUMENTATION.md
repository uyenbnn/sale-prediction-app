# Model Evaluation API Endpoint

## Overview

The **Model Evaluation API** allows you to upload a CSV dataset and evaluate the trained model's performance on that data. This is useful for:
- Testing model performance on new data
- Detecting overfitting
- Analyzing model generalization
- Comparing model performance across different datasets

---

## Endpoint

### `POST /api/model-evaluation/csv`

Upload a CSV file to evaluate the trained model.

#### Request

**Type:** `POST`

**Endpoint:** `http://localhost:8000/api/model-evaluation/csv`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): CSV file to evaluate
  - Must be in `.csv` format
  - Must contain columns matching the training dataset: Date, Customer ID, Gender, Age, Product Category, Quantity, Price per Unit, Total Amount

#### Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "dataset_name": "retail_sales_dataset_test.csv",
  "total_samples": 1000,
  "metrics": {
    "mae": 49.56,
    "rmse": 132.66,
    "r2": 0.9573,
    "mape": 7.79,
    "is_acceptable": true,
    "interpretation": "High R² indicates good generalization"
  },
  "error_statistics": {
    "mean_error": 49.56,
    "median_error": 8.0,
    "std_error": 123.11,
    "max_error": 1300.0,
    "min_error": 0.0,
    "predictions_within_10_percent": 642,
    "predictions_within_20_percent": 802,
    "predictions_within_30_percent": 902
  },
  "sample_predictions": [
    {
      "actual": 87.0,
      "predicted": 90.0,
      "absolute_error": 3.0,
      "error_percentage": 3.45
    },
    {
      "actual": 108.0,
      "predicted": 100.0,
      "absolute_error": 8.0,
      "error_percentage": 7.41
    }
  ],
  "file_uploaded_successfully": true
}
```

---

## How to Use

### 1. **Using cURL**

```bash
curl -X POST "http://localhost:8000/api/model-evaluation/csv" \
  -F "file=@retail_sales_dataset_test.csv"
```

### 2. **Using Python (requests library)**

```python
import requests

url = "http://localhost:8000/api/model-evaluation/csv"
files = {"file": open("retail_sales_dataset_test.csv", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(f"Dataset: {result['dataset_name']}")
print(f"Total Samples: {result['total_samples']}")
print(f"MAE: {result['metrics']['mae']}")
print(f"RMSE: {result['metrics']['rmse']}")
print(f"R²: {result['metrics']['r2']}")
print(f"MAPE: {result['metrics']['mape']}%")
print(f"Status: {result['metrics']['interpretation']}")
```

### 3. **Using Python (httpx library)**

```python
import httpx

url = "http://localhost:8000/api/model-evaluation/csv"
with open("retail_sales_dataset_test.csv", "rb") as f:
    files = {"file": f}
    response = httpx.post(url, files=files)
    result = response.json()
    print(result)
```

### 4. **Using JavaScript (fetch API)**

```javascript
const formData = new FormData();
const fileInput = document.getElementById('fileInput');
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/model-evaluation/csv', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    console.log(`Dataset: ${data.dataset_name}`);
    console.log(`R²: ${data.metrics.r2}`);
    console.log(`Interpretation: ${data.metrics.interpretation}`);
  });
```

### 5. **Using JavaScript (Axios)**

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const formData = new FormData();
formData.append('file', fs.createReadStream('retail_sales_dataset_test.csv'));

axios.post('http://localhost:8000/api/model-evaluation/csv', formData, {
  headers: formData.getHeaders()
})
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

---

## Response Fields Explained

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `dataset_name` | string | Name of the uploaded CSV file |
| `total_samples` | integer | Number of valid records evaluated |
| `metrics` | object | Model performance metrics |
| `error_statistics` | object | Detailed error distribution |
| `sample_predictions` | array | First 50 predictions for inspection |
| `file_uploaded_successfully` | boolean | Whether upload and evaluation succeeded |

### Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `mae` | float | Mean Absolute Error (lower is better) |
| `rmse` | float | Root Mean Squared Error (lower is better) |
| `r2` | float | R² coefficient 0-1 (higher is better) |
| `mape` | float | Mean Absolute Percentage Error % |
| `is_acceptable` | boolean | Whether R² > 0.8 |
| `interpretation` | string | Human-readable analysis |

### Error Statistics Object

| Field | Type | Description |
|-------|------|-------------|
| `mean_error` | float | Average absolute error |
| `median_error` | float | Median absolute error |
| `std_error` | float | Standard deviation of errors |
| `max_error` | float | Maximum absolute error |
| `min_error` | float | Minimum absolute error |
| `predictions_within_10_percent` | integer | Count of predictions with < 10% error |
| `predictions_within_20_percent` | integer | Count of predictions with < 20% error |
| `predictions_within_30_percent` | integer | Count of predictions with < 30% error |

---

## Error Responses

### 400 Bad Request

**Conditions:**
- File is not a CSV
- CSV file is empty
- CSV missing required columns
- Invalid data format

**Example:**
```json
{
  "detail": "File must be a CSV file (.csv)"
}
```

### 503 Service Unavailable

**Condition:** Model not trained yet

**Example:**
```json
{
  "detail": "Model not trained yet. Run training first."
}
```

### 500 Internal Server Error

**Condition:** Server error during processing

**Example:**
```json
{
  "detail": "Model prediction failed: [error details]"
}
```

---

## Interpretation Guide

### R² Score

| Range | Interpretation | Action |
|-------|----------------|--------|
| 0.95-1.00 | Excellent fit | ✅ Use model confidently |
| 0.80-0.95 | Good fit | ✅ Model is acceptable |
| 0.50-0.80 | Moderate fit | ⚠️ Consider improvements |
| 0.00-0.50 | Poor fit | ❌ Model needs retraining |
| < 0.00 | Model worse than mean | ❌ Serious issues |

### MAPE Score

| Range | Quality | Action |
|-------|---------|--------|
| 0-5% | Excellent | ✅ Very accurate |
| 5-10% | Good | ✅ Good accuracy (Your model) |
| 10-20% | Fair | ⚠️ Acceptable for some use cases |
| 20-50% | Poor | ⚠️ Limited usefulness |
| > 50% | Very Poor | ❌ Not usable |

---

## Example Workflow

```bash
# 1. Generate test dataset
cd data
python generate_test_dataset.py

# 2. Start API server
cd ../backend
python -m uvicorn src.api.app:app --reload

# 3. Evaluate with curl
curl -X POST "http://localhost:8000/api/model-evaluation/csv" \
  -F "file=@../data/retail_sales_dataset_test.csv" | jq

# 4. Or use Python script
python evaluate_via_api.py
```

---

## CSV File Format Requirements

Your CSV file must have these columns:

```
Transaction ID, Date, Customer ID, Gender, Age, Product Category, Quantity, Price per Unit, Total Amount
1, 2023-11-24, CUST001, Male, 34, Beauty, 3, 50, 150
2, 2023-02-27, CUST002, Female, 26, Clothing, 2, 500, 1000
```

---

## Testing with Interactive Docs

FastAPI provides interactive API documentation:

1. **Swagger UI:** `http://localhost:8000/docs`
   - Click on the endpoint
   - Click "Try it out"
   - Click "Choose File" to upload CSV
   - Click "Execute"

2. **ReDoc:** `http://localhost:8000/redoc`
   - View detailed API documentation

---

## Tips & Best Practices

1. **Use realistic data** - CSV should have similar structure to training data
2. **Check file size** - Avoid very large files (> 100MB)
3. **Validate CSV first** - Ensure proper formatting
4. **Monitor R² trend** - Track R² over time to detect model drift
5. **Compare results** - Compare evaluation results across datasets
6. **Save results** - Store responses for future reference

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Model not trained yet" | Run `python src/train.py` first |
| "File must be a CSV file" | Ensure file has `.csv` extension |
| "Failed to read CSV file" | Check CSV format and encoding |
| "No valid records to evaluate" | Verify CSV columns match requirements |
| Connection refused | Ensure API server is running on port 8000 |

