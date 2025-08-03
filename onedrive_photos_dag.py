"""
OneDrive Photos DAG for Airflow

This DAG fetches photos from OneDrive for a specific date across multiple years.
It's designed to work with photos synced from iCloud to OneDrive.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Import the OneDrive fetcher
from onedrive_photos_fetcher import fetch_onedrive_photos_airflow

# DAG Configuration
DAG_ID = "onedrive_day_photos"
SCHEDULE_INTERVAL = "0 4 * * *"  # Run at 4:00 AM daily
START_DATE = datetime(2024, 1, 1)

# Configuration
YEARS_BACK = 5  # Number of years to look back
OUTPUT_DIR = "/path/to/homeassistant/media_source/day_of_photos"  # Update this path
TOKEN_FILE = "/path/to/airflow/dags/onedrive_token.pickle"  # Update this path
PHOTOS_FOLDER = "Pictures"  # OneDrive folder containing photos

# Create the DAG
dag = DAG(
    dag_id=DAG_ID,
    description="Fetch photos from OneDrive for this day in history",
    schedule_interval=SCHEDULE_INTERVAL,
    start_date=START_DATE,
    catchup=False,
    tags=["photos", "onedrive", "day-of-photos"],
)

# Define the main task
fetch_photos_task = PythonOperator(
    task_id="fetch_onedrive_photos",
    python_callable=fetch_onedrive_photos_airflow,
    op_kwargs={
        "target_date": "{{ ds }}",  # Airflow execution date
        "years_back": YEARS_BACK,
        "output_dir": OUTPUT_DIR,
        "client_id": "{{ var.value.ONEDRIVE_CLIENT_ID }}",
        "client_secret": "{{ var.value.ONEDRIVE_CLIENT_SECRET }}",
        "token_file": TOKEN_FILE,
        "photos_folder": PHOTOS_FOLDER,
    },
    dag=dag,
)

# Task dependencies (if you add more tasks later)
fetch_photos_task 