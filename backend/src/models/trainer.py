from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, cross_validate, TimeSeriesSplit
from sklearn.pipeline import Pipeline

from src.config import RANDOM_STATE
from src.data.preprocessing import build_preprocessor, prepare_training_data
from src.models.evaluator import evaluate_regression


@dataclass
class TrainingResult:
    best_model_name: str
    best_model: Pipeline
    metrics: dict


def train_and_compare(df: pd.DataFrame) -> TrainingResult:
    prepared = prepare_training_data(df)
    sorted_idx = prepared.dates.sort_values().index
    X = prepared.X.loc[sorted_idx].reset_index(drop=True)
    y = prepared.y.loc[sorted_idx].reset_index(drop=True)

    tscv = TimeSeriesSplit(n_splits=5)

    # Define model candidates with hyperparameter grids for tuning
    model_configs = {
        "ridge": {
            "model": Ridge(random_state=RANDOM_STATE),
            "params": {
                "model__alpha": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
            },
        },
        "random_forest": {
            "model": RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1),
            "params": {
                "model__n_estimators": [300, 500],
                "model__max_depth": [15, 20, 25],
                "model__min_samples_leaf": [1, 2, 4],
            },
        },
    }

    metrics = {}
    best_model_name = ""
    best_model = None
    best_rmse = float("inf")

    for name, config in model_configs.items():
        print(f"\n[Tuning] {name}...")
        
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("model", config["model"]),
            ]
        )

        # GridSearchCV with 5-fold cross-validation
        grid_search = GridSearchCV(
            pipeline,
            config["params"],
            cv=tscv,
            scoring="neg_mean_squared_error",
            n_jobs=1,
            verbose=0,
        )
        grid_search.fit(X, y)
        best_pipeline = grid_search.best_estimator_

        # Cross-validate to get stable metrics
        cv_results = cross_validate(
            best_pipeline,
            X,
            y,
            cv=tscv,
            scoring=["neg_mean_absolute_error", "neg_mean_squared_error"],
            return_train_score=False,
        )

        mae = -cv_results["test_neg_mean_absolute_error"].mean()
        mse = -cv_results["test_neg_mean_squared_error"].mean()
        rmse = mse ** 0.5

        metrics[name] = {
            "mae": round(float(mae), 4),
            "rmse": round(float(rmse), 4),
            "best_params": grid_search.best_params_,
        }

        print(f"[OK] {name}: MAE={mae:.4f}, RMSE={rmse:.4f}")
        print(f"     Best params: {grid_search.best_params_}")

        if rmse < best_rmse:
            best_rmse = rmse
            best_model_name = name
            best_model = best_pipeline

    return TrainingResult(
        best_model_name=best_model_name,
        best_model=best_model,
        metrics={
            "selected_model": best_model_name,
            "metrics": metrics,
        },
    )
