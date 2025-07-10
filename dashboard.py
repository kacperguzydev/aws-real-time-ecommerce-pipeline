import streamlit as st
import pandas as pd
import boto3
import json
import plotly.express as px
from decimal import Decimal

# Config for LocalStack (S3)
s3 = boto3.client("s3", endpoint_url="http://localhost:4566", region_name="eu-west-1")
BUCKET_NAME = "ecommerce-orders-archive"

# Load orders from S3
orders = []
response = s3.list_objects_v2(Bucket=BUCKET_NAME)

for obj in response.get("Contents", []):
    key = obj["Key"]
    if key.endswith(".json") and "athena-results" not in key:
        result = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        data = json.load(result["Body"])
        orders.append(data)

# Convert to DataFrame
df = pd.DataFrame(orders)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Extract only date without time for grouping
df['date_only'] = df['timestamp'].dt.date

# Monitoring: General KPIs
total_revenue = df["amount"].sum()
average_order_value = df["amount"].mean()
total_orders = len(df)
unique_users = df["user_id"].nunique()
orders_over_1000 = (df["amount"] > 1000).sum()

# Streamlit layout
st.title("E-commerce Order Dashboard")

# Display KPIs
st.subheader("General Statistics")
st.write(f"Total revenue: {total_revenue:.2f}")
st.write(f"Average order value: {average_order_value:.2f}")
st.write(f"Number of orders: {total_orders}")
st.write(f"Number of unique users: {unique_users}")
st.write(f"Orders over 1000 units: {orders_over_1000}")

# User-level Summary
st.subheader("User-level Summary")
user_summary = df.groupby("user_id")["amount"].agg(
    total_orders="count",
    total_spent="sum",
    average_order_value="mean",
    max_order_value="max"
).sort_values(by="total_spent", ascending=False)
st.write(user_summary)

# Orders amount distribution
st.subheader("Order Amount Distribution")
fig2 = px.histogram(df, x="amount", nbins=20, title="Distribution of Order Amount")
st.plotly_chart(fig2)

# Top 3 users by total spend
st.subheader("Top 3 Users by Total Spend")
top_users = user_summary.head(3).reset_index()
for i, row in top_users.iterrows():
    st.write(f"{i+1}. {row['user_id']} - {row['total_spent']:.2f} spent")

# Optional: Orders by hour
st.subheader("Orders by Hour")
df["hour"] = df["timestamp"].dt.hour
orders_by_hour = df.groupby("hour").size().rename("order_count")
fig3 = px.bar(orders_by_hour, x=orders_by_hour.index, y=orders_by_hour.values, title="Orders by Hour")
st.plotly_chart(fig3)
