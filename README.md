# Sale Prediction - Small Business Decision Support

This project evaluates whether simple machine learning can help small businesses make better inventory decisions.

## Scope

- Predict next-day sales per product.
- Compare Linear Regression vs Random Forest.
- Serve predictions via FastAPI.
- Show predictions and stock suggestions in Angular.

## Project structure

- backend/: model training and API
- frontend/: Angular integration files
- data/: Kaggle dataset location
- models/: trained model artifacts

## Quick start

1. Put Kaggle CSV at data/retail_sales_dataset.csv.
2. Setup backend dependencies and train model.
3. Start FastAPI.
4. Start Angular app and call API.
