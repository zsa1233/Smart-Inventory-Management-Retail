import pandas as pd
# this code is used later when i want to include all products in admin ui (step 6)
def forecast_all_products(df, predictor, prediction_length=30):
    """
    Forecasts for all products in the DataFrame using the SageMaker DeepAR endpoint.
    
    Args:
        df: DataFrame with columns ['product_id', 'date', 'units_sold']
        predictor: SageMaker predictor object
        prediction_length: Number of days to forecast
    
    Returns:
        DataFrame with columns: ['product_id', 'forecast_day', 'mean', 'q10', 'q90']
    """
    instances = []
    product_ids = df['product_id'].unique()
    for product_id in product_ids:
        product_history = df[df['product_id'] == product_id].sort_values('date')['units_sold'].tolist()
        start_date = str(df[df['product_id'] == product_id]['date'].min().date())
        instances.append({
            "start": start_date,
            "target": product_history
        })

    payload = {
        "instances": instances,
        "configuration": {
            "num_samples": 100,
            "output_types": ["mean", "quantiles"],
            "quantiles": ["0.1", "0.5", "0.9"]
        }
    }

    results = predictor.predict(payload)
    
    # Build a DataFrame of forecasts
    all_forecasts = []
    for i, product_id in enumerate(product_ids):
        mean = results['predictions'][i]['mean']
        q10 = results['predictions'][i]['quantiles']['0.1']
        q90 = results['predictions'][i]['quantiles']['0.9']
        for day in range(prediction_length):
            all_forecasts.append({
                'product_id': product_id,
                'forecast_day': day + 1,
                'mean': mean[day],
                'q10': q10[day],
                'q90': q90[day]
            })
    forecast_df = pd.DataFrame(all_forecasts)
    return forecast_df

# Example usage:
forecast_df = forecast_all_products(df, predictor, prediction_length=30)
print(forecast_df.head())