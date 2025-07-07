import boto3
import pandas as pd
from datetime import datetime
import json

def export_table_to_csv(table_name, s3_bucket, s3_key):
    """
    Export DynamoDB table to CSV and upload to S3
    """
    # Initialize DynamoDB and S3 clients
    dynamodb = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    
    # Get the table
    table = dynamodb.Table(table_name)
    
    # Scan the table to get all items
    print(f"Scanning table {table_name}...")
    response = table.scan()
    items = response['Items']
    
    # Handle pagination if table is large
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    
    print(f"Found {len(items)} items in {table_name}")
    
    # Convert to DataFrame
    df = pd.DataFrame(items)
    
    # Convert the DataFrame to CSV
    csv_data = df.to_csv(index=False)
    
    # Upload to S3
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=csv_data
    )
    
    print(f"Successfully exported {table_name} to s3://{s3_bucket}/{s3_key}")
    return len(items)

def main():
    # Configuration
    s3_bucket = 'smart-inventory-data-1751754698'  # Updated bucket name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export ElectronicsProducts table
    print("Exporting ElectronicsProducts table...")
    electronics_count = export_table_to_csv(
        'ElectronicsProducts',
        s3_bucket,
        f'inventory/electronics_products_{timestamp}.csv'
    )
    
    # Export SalesHistory table
    print("Exporting SalesHistory table...")
    sales_count = export_table_to_csv(
        'SalesHistory',
        s3_bucket,
        f'sales/sales_history_{timestamp}.csv'
    )
    
    print(f"\nExport completed!")
    print(f"ElectronicsProducts: {electronics_count} items")
    print(f"SalesHistory: {sales_count} items")
    print(f"Files saved to s3://{s3_bucket}/")

if __name__ == "__main__":
    main() 