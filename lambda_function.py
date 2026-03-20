
import boto3
import pandas as pd
import io
import json
from datetime import datetime

s3 = boto3.client("s3")

def lambda_handler(event, context):
    """
    Triggered when a new CSV lands in s3://bucket/raw/orders/
    Cleans and transforms the data
    Writes result to s3://bucket/transformed/orders/
    """

# the file that triggered lambda
    bucket   = event["Records"][0]["s3"]["bucket"]["name"]
    raw_key  = event["Records"][0]["s3"]["object"]["key"]
    filename = raw_key.split("/")[-1]

    print(f"Processing: s3://{bucket}/{raw_key}")

    
    response = s3.get_object(Bucket=bucket, Key=raw_key)
    df = pd.read_csv(io.BytesIO(response["Body"].read()))
    print(f"Loaded {len(df)} rows")

#drop duplicates

    df = df.drop_duplicates(subset=["order_id"])

#  Remove cancelled orders
    df_cancelled  = df[df["order_status"] == "Cancelled"].copy()
    df            = df[df["order_status"] != "Cancelled"].copy()

# Fill any null values
    df["discount_pct"]    = df["discount_pct"].fillna(0)
    df["discount_amount"] = df["discount_amount"].fillna(0)

# Add revenue band column
    def revenue_band(amount):
        if amount < 500:    return "Low"
        elif amount < 2000: return "Medium"
        elif amount < 5000: return "High"
        else:               return "Premium"

    df["revenue_band"] = df["total_amount"].apply(revenue_band)

# Add day of week
    df["day_of_week"] = pd.to_datetime(df["order_date"]).dt.day_name()

# Add is_weekend flag
    df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

# Add profit estimate (assume 30% margin)
    df["estimated_profit"] = (df["total_amount"] * 0.30).round(2)

# Standardize city names (title case)
    df["city"]  = df["city"].str.title()
    df["state"] = df["state"].str.title()

# Add processed timestamp
    df["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Transformed {len(df)} active orders")
    print(f"Revenue bands: {df['revenue_band'].value_counts().to_dict()}")

    # Write active orders to transformed/
    transformed_key = f"transformed/orders/transformed_{filename}"
    write_to_s3(df, bucket, transformed_key)
    print(f"Saved transformed data: s3://{bucket}/{transformed_key}")

    # Write cancelled orders separately
    if len(df_cancelled) > 0:
        cancelled_key = f"transformed/cancelled/cancelled_{filename}"
        write_to_s3(df_cancelled, bucket, cancelled_key)
        print(f"Saved cancelled orders: s3://{bucket}/{cancelled_key}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message":          "Transformation complete",
            "active_orders":    len(df),
            "cancelled_orders": len(df_cancelled),
            "output_path":      f"s3://{bucket}/{transformed_key}"
        })
    }


def write_to_s3(df: pd.DataFrame, bucket: str, key: str):
    """Write a DataFrame as CSV directly to S3."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue(),
        ContentType="text/csv"
    )