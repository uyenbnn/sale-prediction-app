#!/usr/bin/env python
"""Quick import test to verify all new modules load correctly."""

try:
    from src.api.schemas import (
        PredictRequest, PredictResponse,
        ForecastDayRow, ForecastSummary, ForecastRangeRequest, ForecastRangeResponse,
        EvaluationRow, AccuracyTrendPoint, EvaluationSummary, EvaluationResponse,
        ProductComparisonMetric, ProductComparisonResponse
    )
    print("✓ All schemas imported successfully")
    
    from src.api.routes.predict import router
    print("✓ Routes imported successfully")
    
    from src.services.recommendation import stock_suggestion
    result = stock_suggestion(250, 200)
    print(f"✓ Recommendation service working: stock_suggestion(250, 200) = '{result}'")
    
    print("\n✅ All backend imports and basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
