from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATE_CANDIDATES = ["date", "transaction_date", "order_date", "invoice_date"]
PRODUCT_CANDIDATES = [
    "product",
    "product_name",
    "item",
    "item_name",
    "category",
    "product category",
]
SALES_CANDIDATES = ["sales", "revenue", "total_sales", "amount", "total amount"]
QTY_CANDIDATES = ["quantity", "qty", "units_sold"]
PRICE_CANDIDATES = ["price", "unit_price", "price per unit"]

FEATURE_COLUMNS = [
    "product",
    "year",
    "quarter",
    "month",
    "weekofyear",
    "day",
    "dayofyear",
    "dayofweek",
    "is_weekend",
    "month_sin",
    "month_cos",
    "dayofweek_sin",
    "dayofweek_cos",
    "avg_price",
    "avg_quantity",
    "avg_age",
    "sales_rolling_7",
    "sales_rolling_30",
]


@dataclass
class TrainingData:
    X: pd.DataFrame
    y: pd.Series
    dates: pd.Series


class DataValidationError(ValueError):
    pass


def _find_column(columns: pd.Index, candidates: list[str]) -> str | None:
    lowered = {c.lower(): c for c in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def _resolve_target(df: pd.DataFrame) -> pd.Series:
    sales_col = _find_column(df.columns, SALES_CANDIDATES)
    if sales_col:
        return pd.to_numeric(df[sales_col], errors="coerce")

    qty_col = _find_column(df.columns, QTY_CANDIDATES)
    price_col = _find_column(df.columns, PRICE_CANDIDATES)
    if qty_col and price_col:
        qty = pd.to_numeric(df[qty_col], errors="coerce")
        price = pd.to_numeric(df[price_col], errors="coerce")
        return qty * price

    raise DataValidationError(
        "Could not infer sales target. Add a sales/revenue column or quantity and price columns."
    )


def prepare_training_data(raw_df: pd.DataFrame) -> TrainingData:
    df = raw_df.copy()
    if df.empty:
        raise DataValidationError("Input dataset is empty.")

    date_col = _find_column(df.columns, DATE_CANDIDATES)
    product_col = _find_column(df.columns, PRODUCT_CANDIDATES)

    if not date_col:
        raise DataValidationError(
            "Could not infer date column. Expected one of: date, transaction_date, order_date, invoice_date."
        )
    if not product_col:
        raise DataValidationError(
            "Could not infer product column. Expected one of: product, product_name, item, item_name, category, product category."
        )

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["target_sales"] = _resolve_target(df)

    df = df.dropna(subset=[date_col, product_col, "target_sales"]).copy()
    if df.empty:
        raise DataValidationError("All rows were dropped during basic cleaning.")

    df = df.sort_values(by=date_col).reset_index(drop=True)

    df["product"] = df[product_col].astype(str).str.strip().replace("", "unknown")
    df["year"] = df[date_col].dt.year
    df["quarter"] = df[date_col].dt.quarter
    df["month"] = df[date_col].dt.month
    df["weekofyear"] = df[date_col].dt.isocalendar().week.astype(int)
    df["day"] = df[date_col].dt.day
    df["dayofyear"] = df[date_col].dt.dayofyear
    df["dayofweek"] = df[date_col].dt.dayofweek
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dayofweek_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dayofweek_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)

    # Domain features: price and quantity
    price_col = _find_column(df.columns, PRICE_CANDIDATES)
    qty_col = _find_column(df.columns, QTY_CANDIDATES)
    age_col = _find_column(df.columns, ["age"])

    if price_col:
        df["avg_price"] = pd.to_numeric(df[price_col], errors="coerce")
        df["avg_price"] = df["avg_price"].fillna(df["avg_price"].median())
    else:
        df["avg_price"] = 0.0

    if qty_col:
        df["avg_quantity"] = pd.to_numeric(df[qty_col], errors="coerce")
        df["avg_quantity"] = df["avg_quantity"].fillna(df["avg_quantity"].median())
    else:
        df["avg_quantity"] = 0.0

    if age_col:
        df["avg_age"] = pd.to_numeric(df[age_col], errors="coerce")
        df["avg_age"] = df["avg_age"].fillna(df["avg_age"].median())
    else:
        df["avg_age"] = 0.0

    # Rolling features: use only prior observations to avoid target leakage.
    prior_sales = df["target_sales"].shift(1)
    df["sales_rolling_7"] = prior_sales.rolling(window=7, min_periods=1).mean()
    df["sales_rolling_30"] = prior_sales.rolling(window=30, min_periods=1).mean()

    # Fill NaN values from rolling features
    for col in ["sales_rolling_7", "sales_rolling_30"]:
        df[col] = df[col].fillna(df[col].median())

    X = df[FEATURE_COLUMNS].copy()
    y = df["target_sales"].copy()
    dates = df[date_col].copy()
    return TrainingData(X=X, y=y, dates=dates)


def build_preprocessor() -> ColumnTransformer:
    numeric_features = [
        "year",
        "quarter",
        "month",
        "weekofyear",
        "day",
        "dayofyear",
        "dayofweek",
        "is_weekend",
        "month_sin",
        "month_cos",
        "dayofweek_sin",
        "dayofweek_cos",
        "avg_price",
        "avg_quantity",
        "avg_age",
        "sales_rolling_7",
        "sales_rolling_30",
    ]
    categorical_features = ["product"]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )


def build_inference_row(
    product: str,
    date_value: str,
    recent_average_sales: float | None = None,
) -> pd.DataFrame:
    dt = pd.to_datetime(date_value, errors="coerce")
    if pd.isna(dt):
        raise DataValidationError("Invalid date format. Use YYYY-MM-DD.")

    return pd.DataFrame(
        [
            {
                "product": product,
                "year": dt.year,
                "quarter": dt.quarter,
                "month": dt.month,
                "weekofyear": int(dt.isocalendar().week),
                "day": dt.day,
                "dayofyear": dt.dayofyear,
                "dayofweek": dt.dayofweek,
                "is_weekend": int(dt.dayofweek >= 5),
                "month_sin": np.sin(2 * np.pi * dt.month / 12),
                "month_cos": np.cos(2 * np.pi * dt.month / 12),
                "dayofweek_sin": np.sin(2 * np.pi * dt.dayofweek / 7),
                "dayofweek_cos": np.cos(2 * np.pi * dt.dayofweek / 7),
                # Keep inference schema aligned with training features.
                "avg_price": 0.0,
                "avg_quantity": 0.0,
                "avg_age": 0.0,
                "sales_rolling_7": float(recent_average_sales or 0.0),
                "sales_rolling_30": float(recent_average_sales or 0.0),
            }
        ]
    )
