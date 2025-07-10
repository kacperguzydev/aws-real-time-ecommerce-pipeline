import boto3
import json
import pandas as pd
from datetime import datetime
import time


def run_monitoring():
    s3 = boto3.client("s3", endpoint_url="http://localhost:4566", region_name="eu-west-1")
    BUCKET = "ecommerce-orders-archive"

    # Load orders from S3
    orders = []
    objects = s3.list_objects_v2(Bucket=BUCKET).get("Contents", [])

    for obj in objects:
        if obj["Key"].endswith(".json"):
            content = s3.get_object(Bucket=BUCKET, Key=obj["Key"])
            data = json.load(content["Body"])
            orders.append(data)

    if not orders:
        print("\nNo orders found.")
        return

    df = pd.DataFrame(orders)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    print("\n--- Realtime Monitoring Metrics ---")
    print(f"Total Orders: {len(df)}")
    print(f"New Orders in Last 5 min: {(df['timestamp'] > datetime.utcnow() - pd.Timedelta(minutes=5)).sum()}")
    print(f"High-value Orders (>1000): {(df['amount'] > 1000).sum()}")
    print(f"Average Order Value: {df['amount'].mean():.2f}")
    print(f"Unique Users: {df['user_id'].nunique()}")

    # Spike detection: Orders in the last minute
    one_minute_ago = datetime.utcnow() - pd.Timedelta(minutes=1)
    recent_orders = df[df['timestamp'] > one_minute_ago]

    recent_spike = len(recent_orders)
    print(f"Orders in last minute: {recent_spike}")

    if recent_spike >= 3:
        print("Potential order spike detected!")

    # Latency between orders
    df = df.sort_values("timestamp")
    df["latency_between_orders"] = df["timestamp"].diff().dt.total_seconds()
    print(f"Average latency between orders: {df['latency_between_orders'].mean():.2f} seconds")


if __name__ == "__main__":
    while True:
        run_monitoring()
        time.sleep(60)
