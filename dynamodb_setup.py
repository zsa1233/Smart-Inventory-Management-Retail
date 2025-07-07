import boto3
import pandas as pd

# AWS region
region = 'us-west-2'

# DynamoDB table name
table_name = 'ElectronicsProducts'

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=region)

# 1. Create the table if it doesn't exist
existing_tables = [t.name for t in dynamodb.tables.all()]
if table_name not in existing_tables:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'product_id', 'KeyType': 'HASH'},  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'product_id', 'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    print("Creating table, please wait...")
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print("Table created!")
else:
    table = dynamodb.Table(table_name)
    print("Table already exists.")

# 2. Load your product data
df = pd.read_csv('electronics_inventory_data.csv')

# 3. Insert one item per product_id
for _, row in df.groupby('product_id').head(1).iterrows():
    item = {
        'product_id': str(row['product_id']),
        'name': str(row.get('name', row['product_id'])),  # Use name if available, else product_id
        'current_stock': int(row['current_stock']),
        'reorder_threshold': int(row['reorder_threshold']),
        # Add more fields as needed
    }
    table.put_item(Item=item)
    print(f"Inserted: {item['product_id']}")

print("All products inserted!")