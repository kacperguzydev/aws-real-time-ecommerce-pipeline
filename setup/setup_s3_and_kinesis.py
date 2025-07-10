import boto3

endpoint = "http://localhost:4566"
region = "eu-west-1"

def create_s3_bucket(bucket_name):
    s3 = boto3.client("s3", endpoint_url=endpoint, region_name=region)
    buckets = s3.list_buckets().get("Buckets", [])
    names = [b["Name"] for b in buckets]

    if bucket_name not in names:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region}
        )
        print(f"Created S3 bucket: {bucket_name}")
    else:
        print(f"S3 bucket already exists: {bucket_name}")

def create_kinesis_stream(stream_name):
    kinesis = boto3.client("kinesis", endpoint_url=endpoint, region_name=region)
    streams = kinesis.list_streams().get("StreamNames", [])

    if stream_name not in streams:
        kinesis.create_stream(StreamName=stream_name, ShardCount=1)
        print(f"Created Kinesis stream: {stream_name}")
    else:
        print(f"Kinesis stream already exists: {stream_name}")

if __name__ == "__main__":
    create_s3_bucket("ecommerce-orders-archive")
    create_kinesis_stream("ecommerce-order-stream")
