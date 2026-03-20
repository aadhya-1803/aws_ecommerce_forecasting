
import boto3
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random
import os


load_dotenv()

AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME        = os.getenv("S3_BUCKET_NAME")
NUM_ORDERS            = 500

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
    raise ValueError(
        " Missing credentials, make sure you have all the acesss keys")

fake = Faker("en_IN")  

# Product Catalog
PRODUCTS = {
    "Electronics": [
        ("Wireless Earbuds",    1299, 4999),
        ("Phone Case",           199,  799),
        ("USB-C Charger",        499, 1499),
        ("Bluetooth Speaker",   1499, 5999),
        ("Laptop Stand",         799, 2499),
        ("Webcam HD",           1999, 5999),
    ],
    "Clothing": [
        ("Men's T-Shirt",        299,  999),
        ("Women's Kurti",        499, 1999),
        ("Denim Jeans",          999, 3499),
        ("Sports Shoes",        1499, 5999),
        ("Casual Sneakers",     1299, 4499),
    ],
    "Home & Kitchen": [
        ("Steel Water Bottle",   299,  799),
        ("Non-stick Pan",        699, 2499),
        ("Coffee Mug Set",       399,  999),
        ("Air Fryer",           2999, 7999),
        ("Dinner Set",          1499, 4999),
    ],
    "Books": [
        ("Python Programming",   399,  799),
        ("Data Science Guide",   499,  999),
        ("Self Help Book",       299,  699),
        ("Fiction Novel",        199,  599),
    ],
    "Beauty": [
        ("Face Moisturizer",     349,  999),
        ("Shampoo 400ml",        249,  699),
        ("Sunscreen SPF50",      299,  899),
        ("Lip Balm Pack",        149,  399),
    ],
}

PAYMENT_METHODS  = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]
ORDER_STATUSES   = ["Delivered", "Delivered", "Delivered", "Shipped", "Processing", "Cancelled"]
INDIAN_CITIES    = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Surat", "Nagpur", "Indore", "Bhopal", "Visakhapatnam",
]


def generate_orders(num_orders: int) -> pd.DataFrame:
    """Generate a DataFrame of fake e-commerce orders."""
    orders = []

    end_date   = datetime.now()
    start_date = end_date - timedelta(days=30)

    for i in range(num_orders):
        category        = random.choice(list(PRODUCTS.keys()))
        product_name, min_price, max_price = random.choice(PRODUCTS[category])
        quantity        = random.randint(1, 5)
        unit_price      = round(random.uniform(min_price, max_price), 2)
        discount_pct    = random.choice([0, 0, 0, 5, 10, 15, 20])
        discount_amount = round(unit_price * quantity * discount_pct / 100, 2)
        total_amount    = round(unit_price * quantity - discount_amount, 2)

        order_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )

        orders.append({
            "order_id":        f"ORD-{100000 + i}",
            "customer_id":     f"CUST-{random.randint(1000, 9999)}",
            "customer_name":   fake.name(),
            "city":            random.choice(INDIAN_CITIES),
            "state":           fake.state(),
            "category":        category,
            "product_name":    product_name,
            "quantity":        quantity,
            "unit_price":      unit_price,
            "discount_pct":    discount_pct,
            "discount_amount": discount_amount,
            "total_amount":    total_amount,
            "payment_method":  random.choice(PAYMENT_METHODS),
            "order_status":    random.choice(ORDER_STATUSES),
            "order_date":      order_date.strftime("%Y-%m-%d"),
            "order_time":      order_date.strftime("%H:%M:%S"),
            "order_hour":      order_date.hour,
            "order_month":     order_date.strftime("%Y-%m"),
        })

    return pd.DataFrame(orders)


def upload_to_s3(df: pd.DataFrame):
    """Save CSV locally and upload to S3 under raw/ folder."""
    today     = datetime.now().strftime("%Y-%m-%d")
    filename  = f"orders_{today}_{datetime.now().strftime('%H%M%S')}.csv"
    s3_key    = f"raw/orders/{filename}"

    df.to_csv(filename, index=False)
    print(f"Saved locally: {filename}  ({len(df)} rows)")

    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    s3.upload_file(filename, S3_BUCKET_NAME, s3_key)
    print(f"Uploaded to S3: s3://{S3_BUCKET_NAME}/{s3_key}")

    os.remove(filename)
    print(f"Local file cleaned up.")

    return s3_key


def preview(df: pd.DataFrame):
    """Print a quick summary of the generated data."""
    print("DATA PREVIEW")
    print(df[["order_id", "product_name", "category", "city", "total_amount", "order_status"]].head(5).to_string(index=False))
    print(f"Total Orders  : {len(df)}")
    print(f"Total Revenue : ₹{df['total_amount'].sum():,.2f}")
    print(f"Categories    : {df['category'].nunique()}")
    print(f"Cities        : {df['city'].nunique()}")
    print(f"Date Range    : {df['order_date'].min()} → {df['order_date'].max()}")



if __name__ == "__main__":

    print("Generating e-commerce orders")
    df = generate_orders(NUM_ORDERS)
    preview(df)

    upload = input("Upload to S3? (y/n): ").strip().lower()
    if upload == "y":
        if S3_BUCKET_NAME == "your-bucket-name":
            print("Please update S3_BUCKET_NAME in your .env file first!")
        else:
            upload_to_s3(df)
            print("Done! Check your S3 bucket under raw/orders/")
    else:
        # Save locally only
        filename = f"orders_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved locally as: {filename}")