from __future__ import annotations

import argparse

import pandas as pd

from src.config import DEFAULT_DATASET, METRICS_PATH, MODEL_PATH
from src.models.artifacts import save_metrics, save_model
from src.models.trainer import train_and_compare


def main() -> None:
    parser = argparse.ArgumentParser(description="Train sales prediction models")
    parser.add_argument(
        "--dataset",
        type=str,
        default=str(DEFAULT_DATASET),
        help="Path to retail sales CSV dataset",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.dataset)
    result = train_and_compare(df)
    save_model(result.best_model, MODEL_PATH)
    save_metrics(result.metrics, METRICS_PATH)

    print("Training complete")
    print(f"Selected model: {result.best_model_name}")
    print(result.metrics)


if __name__ == "__main__":
    main()
