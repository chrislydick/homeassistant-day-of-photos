"""
OneDrive Photos DAG for Airflow 2.10.2

This DAG fetches photos from OneDrive for a specific date across multiple years.
It's designed to work with photos synced from iCloud to OneDrive.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from onedrive_photos_fetcher import fetch_onedrive_photos_airflow

# DAG Configuration
DAG_ID = "onedrive_day_photos"
SCHEDULE_INTERVAL = "0 4 * * *"  # Run at 4:00 AM daily
START_DATE = datetime(2024, 1, 1)

def fetch_photos_function(**context):
    """Fetch photos from OneDrive for this day in history."""
    from airflow.models import Variable
    
    # Get credentials from Airflow variables
    client_id = Variable.get("ONEDRIVE_CLIENT_ID", default_var=None)
    client_secret = Variable.get("ONEDRIVE_CLIENT_SECRET", default_var=None)
    
    if not client_id or not client_secret:
        raise ValueError("ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET must be set in Airflow Variables")
    
    # Call the fetcher function
    fetch_onedrive_photos_airflow(
        target_date=None,  # Use today's date
        years_back=5,
        output_dir="/srv/homeassistant/media/day_photos",
        client_id=client_id,
        client_secret=client_secret,
        token_file="/tmp/onedrive_token.pickle",
        photos_folder="Pictures"
    )
    
    return "Success"

# Create the DAG - Airflow 2.10.2 compatible
dag = DAG(
    dag_id=DAG_ID,
    description="Fetch photos from OneDrive for this day in history",
    schedule_interval=SCHEDULE_INTERVAL,  # Use schedule_interval for 2.10.2
    start_date=START_DATE,
    catchup=False,
    tags=["photos", "onedrive", "day-of-photos"],
)

# Define the main task
fetch_photos_task = PythonOperator(
    task_id="fetch_onedrive_photos",
    python_callable=fetch_photos_function,
    dag=dag,
)

# Set task dependencies
fetch_photos_task 