import boto3
import json
import uuid
import random
import time
from datetime import datetime
from decimal import Decimal  # Import Decimal for DynamoDB

# LocalStack config
endpoint = "http://localhost:4566"
region = "eu-west-1"
state_machine_arn = "arn:aws:states:eu-west-1:000000000000:stateMachine:order-processing-flow"

# Step Functions client
sfn = boto3.client("stepfunctions", endpoint_url=endpoint, region_name=region)
# DynamoDB client
dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint, region_name=region)
# S3 client
s3 = boto3.client("s3", endpoint_url=endpoint, region_name=region)

# DynamoDB table name
TABLE_NAME = "ecommerce_orders"
# S3 bucket
BUCKET_NAME = "ecommerce-orders-archive"

# Sample product catalog with prices (using Decimal for DynamoDB compatibility)
PRODUCT_CATALOG = [
    {"product_id": "wireless_mouse", "name": "Wireless Mouse", "price": Decimal("49.99")},
    {"product_id": "bluetooth_headphones", "name": "Bluetooth Headphones", "price": Decimal("89.99")},
    {"product_id": "laptop_stand", "name": "Laptop Stand", "price": Decimal("39.99")},
    {"product_id": "usb_c_charger", "name": "USB-C Charger", "price": Decimal("29.99")},
    {"product_id": "mechanical_keyboard", "name": "Mechanical Keyboard", "price": Decimal("99.99")},
    {"product_id": "hd_webcam", "name": "HD Webcam", "price": Decimal("74.99")},
    {"product_id": "portable_ssd", "name": "Portable SSD", "price": Decimal("129.99")},
    {"product_id": "smartwatch", "name": "Smartwatch", "price": Decimal("199.99")},
    {"product_id": "office_chair", "name": "Ergonomic Office Chair", "price": Decimal("249.99")},
    {"product_id": "led_desk_lamp", "name": "LED Desk Lamp", "price": Decimal("24.99")}
]

# Get the DynamoDB table
table = dynamodb.Table(TABLE_NAME)


# Custom JSON encoder for Decimal
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")


# Function to generate an order
def generate_order():
    num_items = random.randint(1, 3)
    items = []
    total_amount = Decimal(0)  # Using Decimal for total amount

    for _ in range(num_items):
        product = random.choice(PRODUCT_CATALOG)
        quantity = random.randint(1, 2)
        item_total = product["price"] * quantity
        total_amount += item_total

        items.append({
            "product_id": product["product_id"],
            "product_name": product["name"],
            "unit_price": product["price"],  # Storing price as Decimal
            "quantity": quantity
        })

    order = {
        "order_id": str(uuid.uuid4()),
        "user_id": f"user_{random.randint(1, 10)}",
        "amount": total_amount,  # Amount is also stored as Decimal
        "items": items,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Save the order to DynamoDB
    table.put_item(Item=order)

    # Save the order to S3 (as a JSON file)
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"orders/{order['order_id']}.json",
        Body=json.dumps(order, default=decimal_default),
        ContentType="application/json"
    )

    return order


# Function to start Step Function execution
def start_step_function(order_event):
    response = sfn.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(order_event, default=decimal_default)
    )
    return response


# Continuous stream
print("Starting continuous order generation... Press Ctrl+C to stop.")
try:
    while True:
        order_event = generate_order()

        # Start Step Functions execution
        response = start_step_function(order_event)

        execution_arn = response["executionArn"]
        print(
            f"Started order: {order_event['order_id']} | Amount: {order_event['amount']} | User: {order_event['user_id']}")

        # Check the status of the execution without printing the failed status
        check_response = sfn.describe_execution(
            executionArn=execution_arn
        )

        # Print only when successful
        if check_response['status'] == 'SUCCEEDED':
            print(f"Execution status: {check_response['status']}")

        time.sleep(3)

except KeyboardInterrupt:
    print("Order generation stopped.")
