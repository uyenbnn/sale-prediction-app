from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
CHARTS_DIR = MODEL_DIR / "charts"
MODEL_PATH = MODEL_DIR / "sales_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

DEFAULT_DATASET = DATA_DIR / "retail_sales_dataset.csv"

TEST_RATIO = 0.2
RANDOM_STATE = 42
