"""
Airflow DAG for fetching "on this day" photos from Google Photos.

This DAG runs daily at 4:00 AM to fetch photos from the same day across
multiple years and download them to a local directory for use with
Home Assistant. This solution avoids the 2FA issues common with iCloud.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Import our enhanced Google Photos fetcher
from google_photos_fetcher import fetch_google_photos_airflow

# DAG configuration
DAG_ID = "google_photos_day_photos"
SCHEDULE_INTERVAL = "0 4 * * *"  # Run at 4:00 AM daily
START_DATE = datetime(2024, 1, 1)
DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}

# Configuration parameters
YEARS_BACK = 5
OUTPUT_DIR = "/srv/homeassistant/media/day_photos"  # Adjust this path as needed
CREDENTIALS_FILE = "/opt/airflow/dags/creds.json"  # Path to Google OAuth credentials
TOKEN_FILE = "/opt/airflow/dags/token.pickle"  # Path to token file

# Create the DAG
dag = DAG(
    dag_id=DAG_ID,
    schedule_interval=SCHEDULE_INTERVAL,
    start_date=START_DATE,
    default_args=DEFAULT_ARGS,
    description="Fetch 'on this day' photos from Google Photos",
    catchup=False,
    tags=["google", "photos", "homeassistant"],
)

# Task to fetch photos
fetch_photos_task = PythonOperator(
    task_id="fetch_google_photos",
    python_callable=fetch_google_photos_airflow,
    op_kwargs={
        "target_date": "{{ ds }}",  # Airflow template variable for execution date
        "years_back": YEARS_BACK,
        "output_dir": OUTPUT_DIR,
        "credentials_file": CREDENTIALS_FILE,
        "token_file": TOKEN_FILE,
    },
    dag=dag,
)

# Set task dependencies (if you add more tasks later)
fetch_photos_task

# Alternative configuration using Airflow Variables:
# If you prefer to use Airflow Variables for file paths, replace the op_kwargs above with:
"""
fetch_photos_task = PythonOperator(
    task_id="fetch_google_photos",
    python_callable=fetch_google_photos_airflow,
    op_kwargs={
        "target_date": "{{ ds }}",
        "years_back": YEARS_BACK,
        "output_dir": "{{ var.value.GOOGLE_PHOTOS_OUTPUT_DIR }}",
        "credentials_file": "{{ var.value.GOOGLE_PHOTOS_CREDENTIALS_FILE }}",
        "token_file": "{{ var.value.GOOGLE_PHOTOS_TOKEN_FILE }}",
    },
    dag=dag,
)
"""

# For manual testing, you can also create a simpler version:
"""
def create_simple_dag():
    '''Create a simpler DAG for testing'''
    simple_dag = DAG(
        dag_id="google_photos_simple",
        schedule_interval="0 4 * * *",
        start_date=datetime(2024, 1, 1),
        default_args=DEFAULT_ARGS,
        catchup=False,
    )
    
    PythonOperator(
        task_id="fetch_photos",
        python_callable=fetch_google_photos_airflow,
        op_kwargs={
            "target_date": "{{ ds }}",
            "years_back": 3,  # Shorter range for testing
            "output_dir": "./test_images",
            "credentials_file": "./creds.json",
            "token_file": "./token.pickle",
        },
        dag=simple_dag,
    )
    
    return simple_dag
""" 