import boto3

endpoint = "http://localhost:4566"
region = "eu-west-1"

def create_secret(name, value):
    sm = boto3.client("secretsmanager", endpoint_url=endpoint, region_name=region)
    existing = sm.list_secrets()["SecretList"]
    if not any(secret["Name"] == name for secret in existing):
        sm.create_secret(Name=name, SecretString=value)
        print(f"Created secret: {name}")
    else:
        print(f"Secret already exists: {name}")

if __name__ == "__main__":
    create_secret("payment_api_key", "sk_test_1234567890")
