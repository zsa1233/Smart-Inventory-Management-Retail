import boto3
import pandas as pd
import sagemaker
from sagemaker.predictor import Predictor
import json
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

region = 'us-west-2'

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=region)
inventory_table = dynamodb.Table('ElectronicsProducts')
sales_table = dynamodb.Table('SalesHistory')

# Load inventory from DynamoDB
response = inventory_table.scan()
inventory_df = pd.DataFrame(response['Items'])
print("Inventory DataFrame before forecasting:")
print(inventory_df.head())
print("Number of products:", len(inventory_df))

# Load sales history from DynamoDB
sales_response = sales_table.scan()
sales_df = pd.DataFrame(sales_response['Items'])

# Set up your SageMaker predictor
predictor = Predictor(
    endpoint_name='forecasting-deepar-2025-07-01-11-33-55-356',
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer()
)

# Forecasting loop
for idx, row in inventory_df.iterrows():
    print(f"Processing product {row['product_id']} ({idx+1}/{len(inventory_df)})")
    product_id = row['product_id']
    product_sales = sales_df[sales_df['product_id'] == product_id].sort_values('date')
    history = product_sales['units_sold'].astype(int).tolist()
    start_date = product_sales['date'].min()

    if not history or pd.isna(start_date):
        print(f"Skipping {product_id}: No sales history.")
        continue

    payload = {
        "instances": [
            {
                "start": str(start_date),
                "target": history
            }
        ],
        "configuration": {
            "num_samples": 100,
            "output_types": ["mean"],
        }
    }
    result = predictor.predict(payload)
    forecasted_demand = sum(result['predictions'][0]['mean'])  # sum over forecast horizon

    # Compare with current stock and reorder threshold
    current_stock = int(row['current_stock'])
    reorder_threshold = int(row['reorder_threshold'])
    needs_restock = (forecasted_demand + reorder_threshold) > current_stock

    # Update DynamoDB with restock alert
    inventory_table.update_item(
        Key={'product_id': product_id},
        UpdateExpression='SET restock_needed = :val',
        ExpressionAttributeValues={':val': needs_restock}
    )
    print(f"Product {product_id}: Restock needed? {needs_restock}")

# Load your inventory data
df = pd.read_csv('electronics_inventory_data.csv')

# Insert one item per product_id with inventory fields
for _, row in df.groupby('product_id').head(1).iterrows():
    item = {
        'product_id': str(row['product_id']),
        'current_stock': int(row['current_stock']),
        'reorder_threshold': int(row['reorder_threshold']),
        # Add more fields as needed
    }
    inventory_table.put_item(Item=item)
    print(f"Inserted: {item['product_id']}")

print("Repopulation complete!") 