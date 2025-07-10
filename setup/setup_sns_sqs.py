import boto3

endpoint = "http://localhost:4566"
region = "eu-west-1"

def create_sns_topic(name):
    sns = boto3.client("sns", endpoint_url=endpoint, region_name=region)
    response = sns.create_topic(Name=name)
    print(f"Created SNS topic: {name}")
    return response["TopicArn"]

def create_sqs_queue(name):
    sqs = boto3.client("sqs", endpoint_url=endpoint, region_name=region)
    response = sqs.create_queue(QueueName=name)
    print(f"Created SQS queue: {name}")
    return response["QueueUrl"]

if __name__ == "__main__":
    create_sns_topic("order-alerts")
    create_sqs_queue("order-dlq")
