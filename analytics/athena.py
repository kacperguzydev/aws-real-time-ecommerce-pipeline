import boto3
import json
import pandas as pd

# Connect to LocalStack's S3
s3 = boto3.client("s3", endpoint_url="http://localhost:4566", region_name="eu-west-1")
BUCKET_NAME = "ecommerce-orders-archive"

# Read and load all order JSON files from S3
orders = []
response = s3.list_objects_v2(Bucket=BUCKET_NAME)

for obj in response.get("Contents", []):
    key = obj["Key"]
    if key.endswith(".json") and "athena-results" not in key:
        result = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        data = json.load(result["Body"])
        orders.append(data)

df = pd.DataFrame(orders)
df["timestamp"] = pd.to_datetime(df["timestamp"])

print("\nLoaded order data from S3")
print(f"Total orders: {len(df)}")

# General metrics
total_revenue = df["amount"].sum()
avg_order_value = df["amount"].mean()
num_orders = len(df)
unique_users = df["user_id"].nunique()
high_value_orders = (df["amount"] > 1000).sum()

print("\n--- Overview ---")
print(f"Total revenue: {total_revenue:.2f}")
print(f"Average order value: {avg_order_value:.2f}")
print(f"Unique users: {unique_users}")
print(f"Orders over 1000: {high_value_orders}")

# Metrics per user
print("\n--- Orders by User ---")
user_stats = df.groupby("user_id")["amount"].agg(
    total_orders="count",
    total_spent="sum",
    average_order="mean",
    max_order="max"
).round(2).sort_values(by="total_spent", ascending=False)
print(user_stats.reset_index())

# Daily trends
print("\n--- Orders by Date ---")
daily_orders = df.groupby(df["timestamp"].dt.date).size()
print(daily_orders)

daily_summary = df.groupby(df["timestamp"].dt.date).agg(
    order_count=("order_id", "count"),
    total_revenue=("amount", "sum")
).round(2)
print("\n--- Daily Summary ---")
print(daily_summary)

# Hourly trend
df["hour"] = df["timestamp"].dt.hour
print("\n--- Orders by Hour ---")
print(df.groupby("hour").size())

# Top 3 spenders
print("\n--- Top 3 Users ---")
top_users = user_stats.head(3).reset_index()
for i, row in top_users.iterrows():
    print(f"{i+1}. {row['user_id']} - {row['total_spent']:.2f} total spent")

# Order amount distribution
desc = df["amount"].describe().round(2)
print("\n--- Order Value Statistics ---")
print(f"Min: {desc['min']}")
print(f"25th percentile: {desc['25%']}")
print(f"Median: {desc['50%']}")
print(f"75th percentile: {desc['75%']}")
print(f"Max: {desc['max']}")
