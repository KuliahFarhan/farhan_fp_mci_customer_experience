import os
import pandas as pd
from pathlib import Path
import clickhouse_connect
from dotenv import load_dotenv
import traceback

# Load .env if exists
load_dotenv()

# ClickHouse Configuration
CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CH_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "fp_mci_customer_experience")
CH_USER = os.getenv("CLICKHOUSE_USER", "default")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "password")

# Mapping CSV to Staging Tables
MAPPING = [
    {
        "file": "orders.csv",
        "table": "stg_orders",
        "date_cols": [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    },
    {
        "file": "order_reviews.csv",
        "table": "stg_order_reviews",
        "date_cols": ["review_creation_date", "review_answer_timestamp"]
    },
    {
        "file": "order_items.csv",
        "table": "stg_order_items",
        "date_cols": ["shipping_limit_date"]
    },
    {
        "file": "customers.csv",
        "table": "stg_customers",
        "date_cols": []
    },
    {
        "file": "sellers.csv",
        "table": "stg_sellers",
        "date_cols": []
    },
    {
        "file": "products.csv",
        "table": "stg_products",
        "date_cols": []
    },
    {
        "file": "category_translation.csv",
        "table": "stg_category_translation",
        "date_cols": []
    },
    {
        "file": "order_payments.csv",
        "table": "stg_order_payments",
        "date_cols": []
    },
    {
        "file": "geolocation.csv",
        "table": "stg_geolocation",
        "date_cols": []
    }
]

def get_client():
    """Establish connection to ClickHouse."""
    return clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
        database=CH_DATABASE
    )

def load_table(client, csv_path, table_name, date_columns=None):
    """Load a single CSV file into a ClickHouse staging table."""
    if not csv_path.exists():
        print(f"[SKIP] File not found: {csv_path}")
        return

    # 1. Read CSV
    df = pd.read_csv(csv_path)
    csv_row_count = len(df)

    # 2. Parse Date Columns
    if date_columns:
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    # 3. Handle Missing Values (Convert NaN to None for ClickHouse NULL)
    df = df.where(pd.notnull(df), None)

    # 4. Truncate Table (Idempotency)
    full_table_name = f"{CH_DATABASE}.{table_name}"
    client.command(f"TRUNCATE TABLE {full_table_name}")

    # 5. Insert Data
    client.insert_df(full_table_name, df)

    # 6. Verify Row Count
    result = client.query(f"SELECT count() FROM {full_table_name}")
    ch_row_count = result.result_rows[0][0]

    if csv_row_count != ch_row_count:
        raise ValueError(
            f"Row count mismatch for {table_name}! "
            f"CSV: {csv_row_count}, ClickHouse: {ch_row_count}"
        )

    print(
        f"[OK] {csv_path.name} -> {table_name} | "
        f"CSV rows: {csv_row_count} | ClickHouse rows: {ch_row_count}"
    )

def main():
    print(f"Starting ETL - Loading CSVs to ClickHouse ({CH_HOST}:{CH_PORT})...")
    
    # Path settings
    base_path = Path(__file__).parent.parent
    raw_path = base_path / "data" / "raw"
    
    client = get_client()
    
    try:
        for item in MAPPING:
            csv_file_path = raw_path / item["file"]
            load_table(
                client=client,
                csv_path=csv_file_path,
                table_name=item["table"],
                date_columns=item["date_cols"]
            )
        print("\nAll staging tables loaded successfully!")

    except Exception as e:
        print(f"[ERROR] ETL failed: {repr(e)}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
