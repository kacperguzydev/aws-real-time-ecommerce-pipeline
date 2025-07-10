import boto3
import json

s3 = boto3.client("s3", endpoint_url="http://localhost:4566", region_name="eu-west-1")
kinesis = boto3.client("kinesis", endpoint_url="http://localhost:4566", region_name="eu-west-1")

BUCKET_NAME = "ecommerce-orders-archive"
STREAM_NAME = "ecommerce-order-stream"

def lambda_handler(event, context=None):
    try:
        # Ensure event is a dict
        order = event if isinstance(event, dict) else json.loads(event)

        required_fields = ["order_id", "user_id", "amount", "items", "timestamp"]
        for field in required_fields:
            if field not in order:
                raise ValueError(f"Missing field: {field}")

        # Save to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{order['order_id']}.json",
            Body=json.dumps(order)
        )

        # Send to Kinesis
        kinesis.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(order),
            PartitionKey=order["order_id"]
        )

        print(f"Order validated and sent to stream: {order['order_id']}")

    except Exception as e:
        print("Validation failed:", str(e))
        raise
