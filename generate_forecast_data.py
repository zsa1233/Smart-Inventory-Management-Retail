import boto3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def generate_forecast_data():
    """
    Generate sample forecast data for the next 30 days for all products
    """
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    
    # Get all products from ElectronicsProducts table
    table = dynamodb.Table('ElectronicsProducts')
    response = table.scan()
    products = response['Items']
    
    # Generate forecast data for next 30 days
    forecast_data = []
    start_date = datetime.now() + timedelta(days=1)
    
    for product in products:
        product_id = product['product_id']
        current_stock = product['current_stock']
        reorder_threshold = product['reorder_threshold']
        
        # Generate realistic forecast based on current stock and threshold
        base_demand = max(1, current_stock // 10)  # Base daily demand
        
        for i in range(30):  # Next 30 days
            forecast_date = start_date + timedelta(days=i)
            
            # Add some randomness to make it realistic
            daily_forecast = base_demand + np.random.randint(-2, 3)
            daily_forecast = max(0, daily_forecast)  # Can't be negative
            
            forecast_data.append({
                'product_id': product_id,
                'forecast_date': forecast_date.strftime('%Y-%m-%d'),
                'forecasted_units': daily_forecast,
                'current_stock': current_stock,
                'reorder_threshold': reorder_threshold,
                'stockout_risk': 'HIGH' if current_stock < reorder_threshold else 'LOW'
            })
    
    return forecast_data

def export_forecast_to_s3(forecast_data, s3_bucket):
    """
    Export forecast data to S3 as CSV
    """
    s3_client = boto3.client('s3')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Convert to DataFrame
    df = pd.DataFrame(forecast_data)
    
    # Convert to CSV
    csv_data = df.to_csv(index=False)
    
    # Upload to S3
    s3_key = f'forecasts/forecast_data_{timestamp}.csv'
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=csv_data
    )
    
    print(f"Successfully exported forecast data to s3://{s3_bucket}/{s3_key}")
    return len(forecast_data)

def main():
    s3_bucket = 'smart-inventory-data-1751754698'  # Updated bucket name
    
    print("Generating forecast data...")
    forecast_data = generate_forecast_data()
    
    print("Exporting forecast data to S3...")
    forecast_count = export_forecast_to_s3(forecast_data, s3_bucket)
    
    print(f"\nForecast export completed!")
    print(f"Generated {forecast_count} forecast records")
    print(f"Files saved to s3://{s3_bucket}/forecasts/")

if __name__ == "__main__":
    main() 