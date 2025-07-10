import boto3
import json
import base64
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566", region_name="eu-west-1")
sns = boto3.client("sns", endpoint_url="http://localhost:4566", region_name="eu-west-1")

TABLE_NAME = "ecommerce_orders"
TOPIC_ARN = "arn:aws:sns:eu-west-1:000000000000:order-alerts"


def lambda_handler(event, context=None):
    table = dynamodb.Table(TABLE_NAME)

    for record in event.get("Records", []):
        raw_data = record["kinesis"]["data"]
        decoded_data = base64.b64decode(raw_data).decode("utf-8")
        payload = json.loads(decoded_data, parse_float=Decimal)

        print(f"Processing order: {payload['order_id']}")

        # Ensure amount is Decimal
        if not isinstance(payload["amount"], Decimal):
            payload["amount"] = Decimal(str(payload["amount"]))

        # Save order to DynamoDB
        table.put_item(Item=payload)

        if payload["amount"] > 1000:
            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=f"Order {payload['order_id']} exceeds threshold: {payload['amount']}"
            )
            print(f"Alert sent for order: {payload['order_id']}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Order processed"})
    }
