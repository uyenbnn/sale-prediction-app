import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Read the original dataset
df = pd.read_csv('retail_sales_dataset.csv')

# Create a copy for modification
df_test = df.copy()

# Modify numerical columns with realistic variations to test model precision
# Age: Add random variation (-5 to +5)
df_test['Age'] = df_test['Age'] + np.random.randint(-5, 6, size=len(df_test))
df_test['Age'] = df_test['Age'].clip(lower=18, upper=70)  # Keep realistic age range

# Quantity: Add variation (-2 to +2) but keep minimum of 1
df_test['Quantity'] = df_test['Quantity'] + np.random.randint(-2, 3, size=len(df_test))
df_test['Quantity'] = df_test['Quantity'].clip(lower=1)

# Price per Unit: Add percentage variation (-10% to +10%)
variation = np.random.uniform(0.9, 1.1, size=len(df_test))
df_test['Price per Unit'] = (df_test['Price per Unit'] * variation).round(0).astype(int)
df_test['Price per Unit'] = df_test['Price per Unit'].clip(lower=10)

# Recalculate Total Amount based on new Quantity and Price per Unit
df_test['Total Amount'] = df_test['Quantity'] * df_test['Price per Unit']

# Modify dates: Add random days (-30 to +30) to create distribution variation
date_variation = np.random.randint(-30, 31, size=len(df_test))
df_test['Date'] = pd.to_datetime(df_test['Date']) + pd.to_timedelta(date_variation, unit='D')
df_test['Date'] = df_test['Date'].dt.strftime('%Y-%m-%d')

# Keep Transaction ID and Customer ID the same but shuffle the mapping slightly
# This prevents the model from memorizing patterns

# Save the new dataset
df_test.to_csv('retail_sales_dataset_test.csv', index=False)
print("✓ Test dataset created: retail_sales_dataset_test.csv")
print(f"  Original dataset: {len(df)} rows")
print(f"  Test dataset: {len(df_test)} rows")
print(f"\nSample comparison (first 5 rows):")
print("\nOriginal:")
print(df.head())
print("\nTest Dataset:")
print(df_test.head())
