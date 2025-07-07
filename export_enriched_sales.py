import boto3
import pandas as pd
from datetime import datetime

def get_product_mapping():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ElectronicsProducts')
    response = table.scan()
    items = response['Items']
    # Create a mapping: product_id -> product_name
    return {item['product_id']: item.get('product_name', item['product_id']) for item in items}

def export_enriched_sales_to_s3(s3_bucket, s3_key):
    dynamodb = boto3.resource('dynamodb')
    sales_table = dynamodb.Table('SalesHistory')
    # Scan all sales records
    response = sales_table.scan()
    sales = response['Items']
    while 'LastEvaluatedKey' in response:
        response = sales_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        sales.extend(response['Items'])

    # Convert to DataFrame
    sales_df = pd.DataFrame(sales)
    # Get product mapping
    product_map = get_product_mapping()
    # Add product_name column
    sales_df['product_name'] = sales_df['product_id'].map(product_map)
    # Reorder columns if you want
    cols = ['date', 'product_id', 'product_name', 'units_sold']
    sales_df = sales_df[cols]
    # Export to CSV
    csv_data = sales_df.to_csv(index=False)
    # Upload to S3
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=csv_data)
    print(f"Enriched sales data exported to s3://{s3_bucket}/{s3_key}")

def export_products_to_s3(s3_bucket, s3_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ElectronicsProducts')
    response = table.scan()
    items = response['Items']
    # Convert to DataFrame
    df = pd.DataFrame(items)
    # Ensure column order
    cols = ['product_id', 'product_name', 'current_stock', 'reorder_threshold', 'restock_needed']
    # Only keep columns that exist
    cols = [col for col in cols if col in df.columns]
    df = df[cols]
    # Export to CSV
    csv_data = df.to_csv(index=False)
    # Upload to S3
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=csv_data)
    print(f"Products data exported to s3://{s3_bucket}/{s3_key}")

def export_enriched_forecast_to_s3(s3_bucket, s3_key):
    # Load your forecast data from S3 or however you generate it
    # For this example, let's assume you have a forecast CSV in S3
    forecast_csv_key = 'forecasts/forecast_data_20250705_183225.csv'  # Update with your actual file
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=s3_bucket, Key=forecast_csv_key)
    forecast_df = pd.read_csv(obj['Body'])

    # Get product mapping
    product_map = get_product_mapping()
    # Add product_name column
    forecast_df['product_name'] = forecast_df['product_id'].map(product_map)
    # Reorder columns if you want
    cols = ['forecast_date', 'product_id', 'product_name', 'forecasted_units', 'current_stock', 'reorder_threshold', 'stockout_risk']
    cols = [col for col in cols if col in forecast_df.columns]
    forecast_df = forecast_df[cols]
    # Export to CSV
    csv_data = forecast_df.to_csv(index=False)
    # Upload to S3
    s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=csv_data)
    print(f"Enriched forecast data exported to s3://{s3_bucket}/{s3_key}")

if __name__ == "__main__":
    s3_bucket = 'smart-inventory-data-1751754698'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_key = f'sales/sales_history_enriched_{timestamp}.csv'
    export_enriched_sales_to_s3(s3_bucket, s3_key)
    s3_key = f'inventory/electronics_products_enriched_{timestamp}.csv'
    export_products_to_s3(s3_bucket, s3_key)
    s3_key = f'forecasts/forecast_data_enriched_{timestamp}.csv'
    export_enriched_forecast_to_s3(s3_bucket, s3_key) 