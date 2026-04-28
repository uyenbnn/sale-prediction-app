# Backend

## Setup

1. Create a Python environment.
2. Install dependencies:
   pip install -r requirements.txt

## Dataset

Place your Kaggle CSV at:

../data/retail_sales_dataset.csv

or pass a custom path when training.

## Train

python -m src.train --dataset ../data/retail_sales_dataset.csv

Model and metrics are saved to ../models.

## Run API

uvicorn src.api.app:app --reload --port 8000

## Endpoints

- GET /api/health
- POST /api/predict
