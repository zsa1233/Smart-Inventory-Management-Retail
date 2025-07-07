# Import required libraries
import boto3
import pandas as pd
import os
import json
from datetime import datetime
import subprocess
import sys
import sagemaker
from sagemaker.estimator import Estimator
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput
import matplotlib.pyplot as plt

def check_aws_credentials():
    """
    Check if AWS credentials are configured.
    """
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✓ AWS credentials configured for account: {identity['Account']}")
        print(f"✓ User ARN: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"✗ AWS credentials not configured: {e}")
        return False

def configure_aws():
    """
    Guide user through AWS configuration.
    """
    print("\n=== AWS CONFIGURATION ===")
    print("You need to configure AWS credentials to proceed.")
    print("Please follow these steps:")
    print("1. Go to AWS Console: https://console.aws.amazon.com/")
    print("2. Create an account if you don't have one")
    print("3. Create an IAM user with SageMaker and S3 permissions")
    print("4. Get your Access Key ID and Secret Access Key")
    print("5. Run: aws configure")
    print("\nRequired permissions:")
    print("- AmazonSageMakerFullAccess")
    print("- AmazonS3FullAccess")
    print("- IAMReadOnlyAccess")
    
    input("\nPress Enter when you have configured AWS credentials...")
    
    if check_aws_credentials():
        print("✓ AWS configuration successful!")
        return True
    else:
        print("✗ AWS configuration failed. Please try again.")
        return False

def create_s3_bucket(bucket_name):
    """
    Create S3 bucket for the project.
    """
    try:
        s3 = boto3.client('s3')
        
        # Check if bucket already exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✓ S3 bucket '{bucket_name}' already exists")
            return bucket_name
        except:
            pass
        
        # Create bucket
        print(f"Creating S3 bucket: {bucket_name}")
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        print(f"✓ S3 bucket '{bucket_name}' created successfully")
        return bucket_name
        
    except Exception as e:
        print(f"✗ Error creating S3 bucket: {e}")
        return None

def upload_data_to_s3(bucket_name, file_path):
    """
    Upload data file to S3.
    """
    try:
        s3 = boto3.client('s3')
        
        # Upload file
        s3_key = f"data/{os.path.basename(file_path)}"
        print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
        
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"✓ Data uploaded successfully to s3://{bucket_name}/{s3_key}")
        
        return f"s3://{bucket_name}/{s3_key}"
        
    except Exception as e:
        print(f"✗ Error uploading data: {e}")
        return None

def create_sagemaker_notebook_instance(instance_name, role_arn, bucket_name):
    """
    Create SageMaker notebook instance.
    """
    try:
        sagemaker = boto3.client('sagemaker')
        
        print(f"Creating SageMaker notebook instance: {instance_name}")
        
        response = sagemaker.create_notebook_instance(
            NotebookInstanceName=instance_name,
            InstanceType='ml.t3.medium',  # Small instance for cost efficiency
            RoleArn=role_arn,
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'SmartInventoryManagement'
                }
            ],
            DirectInternetAccess='Enabled'
        )
        
        print(f"✓ SageMaker notebook instance '{instance_name}' creation initiated")
        print("Note: It may take 5-10 minutes for the instance to be ready.")
        
        return instance_name
        
    except Exception as e:
        print(f"✗ Error creating notebook instance: {e}")
        return None

def create_iam_role():
    """
    Create IAM role for SageMaker.
    """
    try:
        iam = boto3.client('iam')
        
        role_name = 'SageMakerInventoryRole'
        
        # Check if role already exists
        try:
            iam.get_role(RoleName=role_name)
            print(f"✓ IAM role '{role_name}' already exists")
            return f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:role/{role_name}"
        except:
            pass
        
        # Create trust policy
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create role
        print(f"Creating IAM role: {role_name}")
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for SageMaker inventory management project'
        )
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'
        ]
        
        for policy in policies:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)
        
        print(f"✓ IAM role '{role_name}' created with required policies")
        
        return response['Role']['Arn']
        
    except Exception as e:
        print(f"✗ Error creating IAM role: {e}")
        return None

def main():
    """
    Main function to set up SageMaker environment.
    """
    print("=== SAGEMAKER SETUP FOR SMART INVENTORY MANAGEMENT ===")
    
    # Check AWS credentials
    if not check_aws_credentials():
        if not configure_aws():
            return
    
    # Create S3 bucket
    bucket_name = f"smart-inventory-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    bucket_name = create_s3_bucket(bucket_name)
    if not bucket_name:
        return
    
    # Upload data to S3
    data_file = "electronics_inventory_data.csv"
    if not os.path.exists(data_file):
        print(f"✗ Data file '{data_file}' not found. Please run data_preparation.py first.")
        return
    
    s3_data_path = upload_data_to_s3(bucket_name, data_file)
    if not s3_data_path:
        return
    
    # Create IAM role
    role_arn = create_iam_role()
    if not role_arn:
        return
    
    # Create SageMaker notebook instance
    instance_name = f"inventory-forecasting-{datetime.now().strftime('%Y%m%d')}"
    notebook_instance = create_sagemaker_notebook_instance(instance_name, role_arn, bucket_name)
    
    if notebook_instance:
        print("\n=== SETUP COMPLETE ===")
        print(f"S3 Bucket: {bucket_name}")
        print(f"Data Location: {s3_data_path}")
        print(f"Notebook Instance: {notebook_instance}")
        print(f"IAM Role: {role_arn}")
        
        print("\n=== NEXT STEPS ===")
        print("1. Wait 5-10 minutes for notebook instance to be ready")
        print("2. Go to AWS SageMaker Console")
        print("3. Open your notebook instance")
        print("4. Create a new notebook for time series forecasting")
        print("5. Use the S3 data path above to load your data")
        
        # Save configuration
        config = {
            'bucket_name': bucket_name,
            's3_data_path': s3_data_path,
            'notebook_instance': notebook_instance,
            'role_arn': role_arn,
            'setup_date': datetime.now().isoformat()
        }
        
        with open('sagemaker_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✓ Configuration saved to sagemaker_config.json")

    # Set up SageMaker session and role
    sagemaker_session = sagemaker.Session(boto_session=boto3.Session(region_name="us-west-2"))
    role = sagemaker.get_execution_role()

    # S3 path to your DeepAR training data
    s3_data_path = "s3://smart-inventory-20250629213619/deepar/deepar_train.json"

    # Output path for model artifacts
    output_path = f"s3://{sagemaker_session.default_bucket()}/deepar/output"

    # DeepAR image URI (for your region)
    container = image_uris.retrieve(framework='forecasting-deepar', region=sagemaker_session.boto_region_name)

    estimator = Estimator(
        image_uri=container,
        role=role,
        instance_count=1,
        instance_type='ml.m5.large',  # You can use 'ml.m5.xlarge' for faster training
        output_path=output_path,
        sagemaker_session=sagemaker_session
    )

    # Set DeepAR hyperparameters (you can tune these later)
    estimator.set_hyperparameters(
        time_freq='D',  # 'D' for daily data
        epochs=50,
        context_length=30,
        prediction_length=30,  # How many days ahead to forecast
        num_layers=2,
        num_cells=40,
        mini_batch_size=32,
        learning_rate=0.001,
        early_stopping_patience=10,
        likelihood='gaussian'
    )

    train_input = TrainingInput(
        s3_data_path,
        content_type='json'
    )

    estimator.fit({'train': train_input})

    # Deploy the trained model as a SageMaker endpoint
    predictor = estimator.deploy(
        initial_instance_count=1,
        instance_type='ml.m5.large',  # or 'ml.m5.xlarge'
        serializer=sagemaker.serializers.JSONSerializer(),
        deserializer=sagemaker.deserializers.JSONDeserializer()
    )

    # Example: Forecast for a single product
    item_id = "ELEC001"
    history = df[df['product_id'] == item_id].sort_values('date')['units_sold'].tolist()

    payload = {
        "instances": [
            {
                "start": str(df[df['product_id'] == item_id]['date'].min().date()),
                "target": history
            }
        ],
        "configuration": {
            "num_samples": 100,
            "output_types": ["mean"],
        }
    }

    result = predictor.predict(payload)
    print(result)

    # Get actual sales history for the product
    actual = df[df['product_id'] == item_id].sort_values('date')['units_sold'].tolist()

    # Get forecasted mean from DeepAR result
    forecast = result['predictions'][0]['mean']

    # Optionally, get quantiles for uncertainty bands
    q10 = result['predictions'][0]['quantiles']['0.1']
    q90 = result['predictions'][0]['quantiles']['0.9']

    # Plot
    plt.figure(figsize=(14, 6))
    plt.plot(range(len(actual)), actual, label='Actual Sales', color='blue')
    plt.plot(range(len(actual), len(actual) + len(forecast)), forecast, label='Forecast (mean)', color='orange')
    plt.fill_between(
        range(len(actual), len(actual) + len(forecast)),
        q10, q90, color='orange', alpha=0.2, label='Forecast 10-90% Quantile'
    )
    plt.xlabel('Day')
    plt.ylabel('Units Sold')
    plt.title(f'Forecast vs. Actual for {item_id}')
    plt.legend()
    plt.show()

    # 1. Get the latest inventory info for each product
    latest_inventory = (
        df.sort_values('date')
          .groupby('product_id')
          .tail(1)
          .set_index('product_id')[['current_stock', 'reorder_threshold']]
    )

    # 2. Calculate total forecasted demand for the next 30 days for each product
    product_ids = df['product_id'].unique()
    forecast_horizon = 30

    forecast_rows = []

    for item_id in product_ids:
        history = df[df['product_id'] == item_id].sort_values('date')['units_sold'].tolist()
        payload = {
            "instances": [
                {
                    "start": str(df[df['product_id'] == item_id]['date'].min().date()),
                    "target": history
                }
            ],
            "configuration": {
                "num_samples": 100,
                "output_types": ["mean"],
            }
        }
        result = predictor.predict(payload)
        # result['predictions'][0]['mean'] is a list of forecasted values for the next 30 days
        for day, mean in enumerate(result['predictions'][0]['mean']):
            forecast_rows.append({
                'product_id': item_id,
                'day': day + 1,
                'mean': mean
            })

    forecast_df = pd.DataFrame(forecast_rows)

    # 3. Merge inventory and forecast
    inventory_forecast = latest_inventory.join(forecast_df.set_index('product_id'))

    # 4. Determine which products need restocking
    inventory_forecast['restock_needed'] = (
        inventory_forecast['forecasted_demand'] + inventory_forecast['reorder_threshold'] > inventory_forecast['current_stock']
    )

    # 5. Show products that need restocking
    restock_alerts = inventory_forecast[inventory_forecast['restock_needed']].reset_index()
    print("Products that need restocking in the next 30 days:")
    print(restock_alerts[['product_id', 'current_stock', 'forecasted_demand', 'reorder_threshold']])

    restock_alerts.to_csv("restock_alerts.csv", index=False)

if __name__ == "__main__":
    main() 