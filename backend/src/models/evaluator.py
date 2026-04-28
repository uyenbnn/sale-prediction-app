from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


@dataclass
class Metrics:
    mae: float
    rmse: float

    def as_dict(self) -> dict:
        return {"mae": round(self.mae, 4), "rmse": round(self.rmse, 4)}


def evaluate_regression(y_true, y_pred) -> Metrics:
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return Metrics(mae=mae, rmse=rmse)
