import boto3

endpoint = "http://localhost:4566"
region = "eu-west-1"

def create_table(table_name):
    dynamodb = boto3.client("dynamodb", endpoint_url=endpoint, region_name=region)
    tables = dynamodb.list_tables().get("TableNames", [])

    if table_name not in tables:
        dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {"AttributeName": "order_id", "AttributeType": "S"}
            ],
            KeySchema=[
                {"AttributeName": "order_id", "KeyType": "HASH"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        print(f"Created DynamoDB table: {table_name}")
    else:
        print(f"DynamoDB table already exists: {table_name}")

if __name__ == "__main__":
    create_table("ecommerce_orders")
