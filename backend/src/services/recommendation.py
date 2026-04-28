def stock_suggestion(predicted_sales: float, recent_average_sales: float | None = None) -> str:
    baseline = recent_average_sales if recent_average_sales and recent_average_sales > 0 else predicted_sales

    high_threshold = baseline * 1.2
    low_threshold = baseline * 0.8

    if predicted_sales > high_threshold:
        return "Increase stock"
    if predicted_sales < low_threshold:
        return "Reduce inventory"
    return "Maintain stock"
