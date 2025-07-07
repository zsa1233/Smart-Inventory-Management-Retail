import boto3

# Mapping of product_id to product_name
PRODUCT_NAMES = {
    "ELEC001": "Samsung 55\" 4K TV",
    "ELEC002": "Apple iPhone 14",
    "ELEC003": "Sony PlayStation 5",
    "ELEC004": "Dell XPS 13 Laptop",
    "ELEC005": "Apple iPad Pro",
    "ELEC006": "Bose QuietComfort 45",
    "ELEC007": "Canon EOS R10 Camera",
    "ELEC008": "Google Nest Hub",
    "ELEC009": "Microsoft Xbox Series X",
    "ELEC010": "LG 65\" OLED TV",
    "ELEC011": "Amazon Echo Dot",
    "ELEC012": "HP Envy 6055e Printer",
    "ELEC013": "Fitbit Versa 4",
    "ELEC014": "Nintendo Switch OLED",
    "ELEC015": "JBL Flip 6 Bluetooth Speaker"
}

def update_product_names():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ElectronicsProducts')
    
    for product_id, product_name in PRODUCT_NAMES.items():
        print(f"Updating {product_id} with name '{product_name}'...")
        table.update_item(
            Key={"product_id": product_id},
            UpdateExpression="SET product_name = :n",
            ExpressionAttributeValues={":n": product_name}
        )
    print("All product names updated!")

if __name__ == "__main__":
    update_product_names() 