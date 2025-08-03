"""
Airflow DAG for fetching "on this day" photos from iCloud.

This DAG runs daily at 4:00 AM to fetch photos from the same day across
multiple years and download them to a local directory for use with
Home Assistant.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Import our enhanced photo fetcher
from icloud_photo_fetcher import fetch_photos_airflow

# DAG configuration
DAG_ID = "icloud_day_photos"
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
SESSION_FILE = "/tmp/icloud_session.pickle"  # Session file location

# Create the DAG
dag = DAG(
    dag_id=DAG_ID,
    schedule_interval=SCHEDULE_INTERVAL,
    start_date=START_DATE,
    default_args=DEFAULT_ARGS,
    description="Fetch 'on this day' photos from iCloud",
    catchup=False,
    tags=["icloud", "photos", "homeassistant"],
)

# Task to fetch photos
fetch_photos_task = PythonOperator(
    task_id="fetch_icloud_photos",
    python_callable=fetch_photos_airflow,
    op_kwargs={
        "target_date": "{{ ds }}",  # Airflow template variable for execution date
        "years_back": YEARS_BACK,
        "output_dir": OUTPUT_DIR,
        "username": "{{ var.value.ICLOUD_USERNAME }}",
        "password": "{{ var.value.ICLOUD_PASSWORD }}",
        "session_file": SESSION_FILE,
    },
    dag=dag,
)

# Set task dependencies (if you add more tasks later)
fetch_photos_task

# Alternative configuration using Airflow Connections instead of Variables:
# If you prefer to use Airflow Connections, replace the op_kwargs above with:
"""
fetch_photos_task = PythonOperator(
    task_id="fetch_icloud_photos",
    python_callable=fetch_photos_airflow,
    op_kwargs={
        "target_date": "{{ ds }}",
        "years_back": YEARS_BACK,
        "output_dir": OUTPUT_DIR,
        "username": "{{ conn.icloud.login }}",
        "password": "{{ conn.icloud.password }}",
        "session_file": SESSION_FILE,
    },
    dag=dag,
)
"""

# For manual testing, you can also create a simpler version:
"""
def create_simple_dag():
    '''Create a simpler DAG for testing'''
    simple_dag = DAG(
        dag_id="icloud_photos_simple",
        schedule_interval="0 4 * * *",
        start_date=datetime(2024, 1, 1),
        default_args=DEFAULT_ARGS,
        catchup=False,
    )
    
    PythonOperator(
        task_id="fetch_photos",
        python_callable=fetch_photos_airflow,
        op_kwargs={
            "target_date": "{{ ds }}",
            "years_back": 3,  # Shorter range for testing
            "output_dir": "./test_images",
            "username": "your_apple_id@example.com",  # Replace with actual
            "password": "your_app_specific_password",  # Replace with actual
        },
        dag=simple_dag,
    )
    
    return simple_dag
""" 