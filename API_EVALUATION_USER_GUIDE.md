# Model Evaluation API - User Guide

## Quick Start

### 1. Start the API Server
```bash
cd backend
python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

### 2. Test the API
```bash
cd backend
python test_evaluation_api.py --url http://127.0.0.1:8000 --file ../data/retail_sales_dataset_test.csv
```

### 3. View Interactive Docs
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## What's New?

### New API Endpoint: `POST /api/model-evaluation/csv`

Users can now:
✅ Upload their own CSV datasets
✅ Get model evaluation metrics (MAE, RMSE, R², MAPE)
✅ See error distribution analysis
✅ Get sample predictions
✅ Detect overfitting automatically

---

## How to Use

### Option 1: Python with requests
```python
import requests

url = "http://127.0.0.1:8000/api/model-evaluation/csv"
files = {"file": open("retail_sales_dataset_test.csv", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(f"R²: {result['metrics']['r2']}")
print(f"MAE: {result['metrics']['mae']}")
```

### Option 2: cURL
```bash
curl -X POST "http://127.0.0.1:8000/api/model-evaluation/csv" \
  -F "file=@retail_sales_dataset_test.csv"
```

### Option 3: Swagger UI (Browser)
1. Go to http://127.0.0.1:8000/docs
2. Find `/api/model-evaluation/csv`
3. Click "Try it out"
4. Upload your CSV file
5. Click "Execute"

---

## Response Example

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
    "std_error": 123.05,
    "max_error": 1300.0,
    "min_error": 0.0,
    "predictions_within_10_percent": 827,
    "predictions_within_20_percent": 890,
    "predictions_within_30_percent": 965
  },
  "sample_predictions": [
    {
      "actual": 87.0,
      "predicted": 90.0,
      "absolute_error": 3.0,
      "error_percentage": 3.45
    },
    ...
  ],
  "file_uploaded_successfully": true
}
```

---

## CSV File Requirements

Your CSV must have these columns:
- `Date` (format: YYYY-MM-DD)
- `Customer ID`
- `Gender` (Male/Female)
- `Age` (numeric)
- `Product Category` (Beauty, Clothing, Electronics, etc.)
- `Quantity` (numeric)
- `Price per Unit` (numeric)
- `Total Amount` (numeric)

Example:
```csv
Transaction ID,Date,Customer ID,Gender,Age,Product Category,Quantity,Price per Unit,Total Amount
1,2023-11-24,CUST001,Male,34,Beauty,3,50,150
2,2023-02-27,CUST002,Female,26,Clothing,2,500,1000
```

---

## Understanding Results

### Metrics Explained

| Metric | Good Range | Your Model | Rating |
|--------|-----------|-----------|--------|
| **R²** | > 0.8 | 0.9573 | ✅ Excellent |
| **MAE** | < 50 | 49.56 | ✅ Good |
| **RMSE** | < 150 | 132.66 | ✅ Good |
| **MAPE** | < 10% | 7.79% | ✅ Good |

### Error Distribution

Your model shows:
- ✅ 82.7% of predictions within 10% error
- ✅ 89.0% of predictions within 20% error
- ✅ 96.5% of predictions within 30% error

---

## Use Cases

### 1. Test on New Data
```bash
# Generate test dataset
cd data && python generate_test_dataset.py

# Evaluate via API
cd backend && python test_evaluation_api.py
```

### 2. Compare Multiple Datasets
```bash
# Test on different CSVs
python test_evaluation_api.py --file dataset1.csv
python test_evaluation_api.py --file dataset2.csv
```

### 3. Monitor Model Drift
```bash
# Run evaluation regularly on new data
python test_evaluation_api.py --file recent_sales.csv
```

---

## API Integration Examples

### JavaScript (React)
```javascript
async function evaluateModel(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://127.0.0.1:8000/api/model-evaluation/csv', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  console.log(`Model R²: ${result.metrics.r2}`);
  return result;
}
```

### Node.js
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const formData = new FormData();
formData.append('file', fs.createReadStream('data.csv'));

const response = await axios.post(
  'http://127.0.0.1:8000/api/model-evaluation/csv',
  formData,
  { headers: formData.getHeaders() }
);

console.log(response.data);
```

### HTML Form
```html
<form id="evalForm">
  <input type="file" name="file" accept=".csv" required>
  <button type="submit">Evaluate Model</button>
  <div id="results"></div>
</form>

<script>
document.getElementById('evalForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  
  const response = await fetch('http://127.0.0.1:8000/api/model-evaluation/csv', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  document.getElementById('results').innerHTML = `
    <h3>Results</h3>
    <p>R²: ${data.metrics.r2}</p>
    <p>MAE: ${data.metrics.mae}</p>
  `;
});
</script>
```

---

## Workflow Examples

### Example 1: Test New Dataset
```bash
# Generate test dataset with variations
cd data
python generate_test_dataset.py

# Evaluate via API
cd ../backend
python test_evaluation_api.py

# Output:
# 📊 Model Evaluation Results
# ✅ Status: High R² indicates good generalization
# 📊 Prediction Accuracy: 82.7% within 10% error
```

### Example 2: Compare Multiple Evaluations
```bash
# Test on different data variations
python test_evaluation_api.py --file ../data/dataset_v1.csv > eval_v1.json
python test_evaluation_api.py --file ../data/dataset_v2.csv > eval_v2.json
python test_evaluation_api.py --file ../data/dataset_v3.csv > eval_v3.json

# Compare results
diff eval_v1.json eval_v2.json
```

### Example 3: Production Monitoring
```bash
# Daily evaluation on latest data
0 9 * * * cd /path/to/backend && \
  python test_evaluation_api.py \
  --file /data/daily_sales.csv \
  >> /logs/eval_$(date +\%Y\%m\%d).log
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Model not trained yet" | Model missing | Run `python src/train.py` |
| "File must be a CSV file" | Wrong format | Use `.csv` extension |
| "Failed to read CSV file" | Invalid format | Check CSV encoding/structure |
| "No valid records" | Missing columns | Verify CSV has all required columns |
| Connection refused | Server not running | Start server: `uvicorn src.api.app:app` |

---

## Files Created/Modified

### New Files
- `backend/src/api/routes/model_evaluation.py` - Evaluation endpoint
- `backend/test_evaluation_api.py` - Test script
- `backend/API_DOCUMENTATION.md` - Detailed API docs

### Modified Files
- `backend/src/api/app.py` - Included evaluation router
- `backend/src/api/schemas.py` - Added evaluation schemas

---

## Next Steps

1. ✅ Start the API server
2. ✅ Test with provided test dataset
3. ✅ Upload your own CSV files
4. ✅ Monitor model performance
5. ✅ Integrate into your application

---

## Support

For issues or questions:
1. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API docs
2. View interactive docs at http://127.0.0.1:8000/docs
3. Review test script: `test_evaluation_api.py`

