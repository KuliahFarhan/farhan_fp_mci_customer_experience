import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import clickhouse_connect
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

# --- Configuration ---
CH_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CH_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "fp_mci_customer_experience")
CH_USER = os.getenv("CLICKHOUSE_USER", "default")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "password")

RAW_DATA_PATH = Path("/opt/airflow/data/raw")
SQL_PATH = Path("/opt/airflow/sql")
SCRIPTS_PATH = Path("/opt/airflow/scripts")

REQUIRED_FILES = [
    "orders.csv",
    "order_reviews.csv",
    "order_items.csv",
    "customers.csv",
    "sellers.csv",
    "products.csv",
    "category_translation.csv",
    "order_payments.csv"
]

# --- Helper Functions ---
def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
        database=CH_DATABASE
    )

def validate_raw_files_func():
    print(f"Checking raw files in {RAW_DATA_PATH}...")
    missing_files = []
    for file_name in REQUIRED_FILES:
        path = RAW_DATA_PATH / file_name
        if not path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        raise FileNotFoundError(f"Missing required raw files: {', '.join(missing_files)}")
    
    print("All required raw files are present.")

def run_sql_file_func(sql_file_relative_path):
    client = get_clickhouse_client()
    sql_file_path = SQL_PATH / sql_file_relative_path
    
    print(f"Executing SQL file: {sql_file_path}")
    if not sql_file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")
    
    with open(sql_file_path, 'r') as f:
        queries = f.read().split(';')
        for query in queries:
            if query.strip():
                client.command(query)
    client.close()
    print(f"Successfully executed: {sql_file_relative_path}")

def run_load_script_func():
    script_path = SCRIPTS_PATH / "load_csv_to_clickhouse.py"
    print(f"Running load script: {script_path}")
    
    # Set environment variables for the subprocess to ensure correct connection
    env = os.environ.copy()
    env["CLICKHOUSE_HOST"] = CH_HOST
    env["CLICKHOUSE_PORT"] = str(CH_PORT)
    env["CLICKHOUSE_DATABASE"] = CH_DATABASE
    env["CLICKHOUSE_USER"] = CH_USER
    env["CLICKHOUSE_PASSWORD"] = CH_PASSWORD
    
    result = subprocess.run(
        ["python", str(script_path)],
        capture_output=True,
        text=True,
        env=env
    )
    
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        raise RuntimeError(f"Script failed with return code {result.returncode}")

def validate_pipeline_outputs_func():
    client = get_clickhouse_client()
    
    # 1. Basic Row Count Validation (Ensure tables are not empty)
    tables_to_check = [
        "stg_orders",
        "stg_order_reviews",
        "stg_order_items",
        "mart_customer_experience_orders",
        "mart_customer_experience_items",
        "mart_monthly_review",
        "mart_delivery_performance"
    ]
    
    print("--- [1] Table Row Count Validation ---")
    for table in tables_to_check:
        res = client.query(f"SELECT count() FROM {CH_DATABASE}.{table}")
        count = res.result_rows[0][0]
        print(f"Table {table}: {count} rows")
        if count == 0:
            raise ValueError(f"CRITICAL: Table {table} is empty!")

    # 2. Review Score Integrity Validation (Order Mart)
    print("\n--- [2] Review Data Integrity Validation (mart_customer_experience_orders) ---")
    
    # Check for invalid score 0
    res_zero = client.query(f"SELECT count() FROM {CH_DATABASE}.mart_customer_experience_orders WHERE review_score = 0")
    count_zero = res_zero.result_rows[0][0]
    print(f"Orders with review_score 0: {count_zero}")
    if count_zero > 0:
        raise ValueError(f"DATA BUG: Found {count_zero} rows with review_score=0. Score should be 1-5 or NULL.")

    # Check for legitimate NULLs (Expected: 768)
    res_null = client.query(f"SELECT count() FROM {CH_DATABASE}.mart_customer_experience_orders WHERE review_score IS NULL")
    count_null = res_null.result_rows[0][0]
    print(f"Orders with review_score NULL (Legitimate): {count_null}")
    if count_null != 768:
        print(f"Warning: Expected 768 NULLs, found {count_null}. Verify if raw data has changed.")

    # 3. Monthly Review Trend Validation
    print("\n--- [3] Analytics Mart Validation (mart_monthly_review) ---")
    
    # Check for invalid 1970 date
    res_date = client.query(f"SELECT count() FROM {CH_DATABASE}.mart_monthly_review WHERE review_month = '1970-01-01'")
    count_1970 = res_date.result_rows[0][0]
    print(f"Rows with review_month '1970-01-01': {count_1970}")
    if count_1970 > 0:
        raise ValueError(f"DATA BUG: Found {count_1970} rows with default date 1970-01-01 in monthly mart.")

    # Check Sum of Reviewed Orders (Expected: 98673)
    res_total = client.query(f"SELECT sum(reviewed_orders) FROM {CH_DATABASE}.mart_monthly_review")
    total_reviewed = res_total.result_rows[0][0]
    print(f"Total Reviewed Orders in Mart: {total_reviewed}")
    
    if total_reviewed == 99441:
        raise ValueError("DATA BUG: Monthly mart is counting all orders (99441) including those without reviews!")
    
    if total_reviewed != 98673:
        print(f"Warning: Total reviewed orders ({total_reviewed}) differs from target 98673.")
    
    client.close()
    print("\n[SUCCESS] Pipeline output validation completed with data integrity checks.")

# --- DAG Definition ---
default_args = {
    "owner": "farhan",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dag_customer_experience_pipeline",
    default_args=default_args,
    description="End-to-end pipeline (CSV to Staging to Mart) for MCI Customer Experience",
    schedule=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["mci", "customer_experience", "clickhouse"],
) as dag:

    start = EmptyOperator(task_id="start")

    validate_raw_files = PythonOperator(
        task_id="validate_raw_files",
        python_callable=validate_raw_files_func,
    )

    create_ch_db = PythonOperator(
        task_id="create_clickhouse_database",
        python_callable=run_sql_file_func,
        op_kwargs={"sql_file_relative_path": "ddl/01_create_database.sql"},
    )

    create_stg_tables = PythonOperator(
        task_id="create_staging_tables",
        python_callable=run_sql_file_func,
        op_kwargs={"sql_file_relative_path": "ddl/02_create_staging_tables.sql"},
    )

    load_csv_to_stg = PythonOperator(
        task_id="load_csv_to_staging",
        python_callable=run_load_script_func,
    )

    create_mart_tables = PythonOperator(
        task_id="create_mart_tables",
        python_callable=run_sql_file_func,
        op_kwargs={"sql_file_relative_path": "ddl/03_create_mart_tables.sql"},
    )

    build_mart_orders = PythonOperator(
        task_id="build_customer_experience_orders",
        python_callable=run_sql_file_func,
        op_kwargs={"sql_file_relative_path": "etl/02_build_customer_experience_orders.sql"},
    )

    build_mart_items = PythonOperator(
        task_id="build_customer_experience_items",
        python_callable=run_sql_file_func,
        op_kwargs={"sql_file_relative_path": "etl/03_build_customer_experience_items.sql"},
    )

    build_monthly_trend = PythonOperator(
        task_id="build_monthly_review_trend",
        python_callable=run_sql_file_func,
        op_kwargs={"sql_file_relative_path": "analytics/01_monthly_review_trend.sql"},
    )

    build_delivery_perf = PythonOperator(
        task_id="build_delivery_performance",
        python_callable=run_sql_file_func,
        op_kwargs={"sql_file_relative_path": "analytics/02_delivery_performance.sql"},
    )

    validate_outputs = PythonOperator(
        task_id="validate_pipeline_outputs",
        python_callable=validate_pipeline_outputs_func,
    )

    end = EmptyOperator(task_id="end")

    # --- Task Dependencies ---
    start >> validate_raw_files >> create_ch_db >> create_stg_tables >> load_csv_to_stg >> \
    create_mart_tables >> build_mart_orders >> build_mart_items >> \
    build_monthly_trend >> build_delivery_perf >> validate_outputs >> end
