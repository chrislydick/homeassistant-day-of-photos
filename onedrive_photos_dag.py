"""
OneDrive Photos DAG for Airflow

This DAG fetches photos from OneDrive for a specific date across multiple years.
It's designed to work with photos synced from iCloud to OneDrive.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import os

# Import the OneDrive fetcher with error handling
try:
    from onedrive_photos_fetcher import fetch_onedrive_photos_airflow
except ImportError as e:
    print(f"Warning: Could not import onedrive_photos_fetcher: {e}")
    # Create a dummy function to prevent DAG loading errors
    def fetch_onedrive_photos_airflow(**kwargs):
        print("OneDrive fetcher not available")
        return None

# DAG Configuration
DAG_ID = "onedrive_day_photos"
SCHEDULE_INTERVAL = "0 4 * * *"  # Run at 4:00 AM daily
START_DATE = datetime(2024, 1, 1)

# Configuration - use environment variables or defaults
YEARS_BACK = int(os.getenv('ONEDRIVE_YEARS_BACK', '5'))
OUTPUT_DIR = os.getenv('ONEDRIVE_OUTPUT_DIR', '/path/to/homeassistant/media_source/day_of_photos')
TOKEN_FILE = os.getenv('ONEDRIVE_TOKEN_FILE', '/path/to/airflow/dags/onedrive_token.pickle')
PHOTOS_FOLDER = os.getenv('ONEDRIVE_PHOTOS_FOLDER', 'Pictures')

# Create the DAG
dag = DAG(
    dag_id=DAG_ID,
    description="Fetch photos from OneDrive for this day in history",
    schedule=SCHEDULE_INTERVAL,  # Fixed: was schedule_interval
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

# Set task dependencies (this line was incomplete)
fetch_photos_task 