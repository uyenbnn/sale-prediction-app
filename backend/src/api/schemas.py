from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    product: str = Field(min_length=1, max_length=200)
    date: str = Field(description="Prediction date in YYYY-MM-DD format")
    recent_average_sales: float | None = Field(default=None, ge=0)


class PredictResponse(BaseModel):
    product: str
    date: str
    predicted_sales: float
    suggestion: str
    selected_model: str | None = None


class ForecastDayRow(BaseModel):
    date: str
    predicted_sales: float
    suggestion: str


class ForecastSummary(BaseModel):
    total_days: int
    avg_predicted_sales: float
    increase_stock_count: int
    reduce_inventory_count: int
    maintain_stock_count: int


class ForecastRangeRequest(BaseModel):
    product: str = Field(min_length=1, max_length=200)
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")
    recent_average_sales: float | None = Field(default=None, ge=0)


class ForecastRangeResponse(BaseModel):
    daily_rows: list[ForecastDayRow]
    summary: ForecastSummary
    selected_model: str | None = None


class EvaluationRow(BaseModel):
    date: str
    product: str
    actual_sales: float
    predicted_sales: float
    absolute_error: float
    error_percentage: float


class AccuracyTrendPoint(BaseModel):
    period: str
    mae: float
    rmse: float
    mape: float


class EvaluationSummary(BaseModel):
    total_samples: int
    overall_mae: float
    overall_rmse: float
    overall_mape: float
    best_product: str
    worst_product: str


class EvaluationResponse(BaseModel):
    evaluation_rows: list[EvaluationRow]
    summary: EvaluationSummary
    accuracy_trend: list[AccuracyTrendPoint]
    chart_image_url: str | None = None
    chart_image_path: str | None = None


class ProductComparisonMetric(BaseModel):
    product: str
    total_days: int
    avg_predicted_sales: float
    sum_predicted_sales: float
    increase_stock_count: int
    reduce_inventory_count: int
    maintain_stock_count: int


class ProductComparisonResponse(BaseModel):
    comparison_metrics: list[ProductComparisonMetric]
    highest_demand_product: str
    highest_demand_average_sales: float
    selected_model: str | None = None
