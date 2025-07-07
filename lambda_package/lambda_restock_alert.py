import boto3
import pandas as pd
import os
import json

def lambda_handler(event, context):
    region = os.environ.get('AWS_REGION', 'us-west-2')
    inventory_table_name = os.environ.get('INVENTORY_TABLE', 'ElectronicsProducts')
    sales_table_name = os.environ.get('SALES_TABLE', 'SalesHistory')
    sagemaker_endpoint = os.environ.get('SAGEMAKER_ENDPOINT', 'forecasting-deepar-2025-07-01-11-33-55-356')
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

    dynamodb = boto3.resource('dynamodb', region_name=region)
    sns = boto3.client('sns', region_name=region)
    inventory_table = dynamodb.Table(inventory_table_name)
    sales_table = dynamodb.Table(sales_table_name)

    # Load inventory
    inventory = inventory_table.scan()['Items']
    inventory_df = pd.DataFrame(inventory)

    # Load sales history
    sales = sales_table.scan()['Items']
    sales_df = pd.DataFrame(sales)

    runtime = boto3.client('sagemaker-runtime')

    for idx, row in inventory_df.iterrows():
        product_id = row['product_id']
        product_sales = sales_df[sales_df['product_id'] == product_id].sort_values('date')
        history = product_sales['units_sold'].astype(int).tolist()
        start_date = product_sales['date'].min()

        if not history or pd.isna(start_date):
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
        response = runtime.invoke_endpoint(
            EndpointName=sagemaker_endpoint,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        result = json.loads(response['Body'].read())
        forecasted_demand = sum(result['predictions'][0]['mean'])

        current_stock = int(row['current_stock'])
        reorder_threshold = int(row['reorder_threshold'])
        needs_restock = (forecasted_demand + reorder_threshold) > current_stock

        if needs_restock:
            message = (
                f"Product {product_id} needs restocking! "
                f"Current stock: {current_stock}, "
                f"Forecasted demand: {forecasted_demand:.0f}, "
                f"Reorder threshold: {reorder_threshold}"
            )
            if sns_topic_arn:
                sns.publish(
                    TopicArn=sns_topic_arn,
                    Message=message,
                    Subject=f"Restock Alert: {product_id}"
                )
            inventory_table.update_item(
                Key={'product_id': product_id},
                UpdateExpression='SET restock_needed = :val',
                ExpressionAttributeValues={':val': True}
            )
        else:
            inventory_table.update_item(
                Key={'product_id': product_id},
                UpdateExpression='SET restock_needed = :val',
                ExpressionAttributeValues={':val': False}
            )
    return {"status": "done"} 