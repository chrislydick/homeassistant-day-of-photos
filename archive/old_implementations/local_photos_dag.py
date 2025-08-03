"""
Airflow DAG for fetching "on this day" photos from local photo library.

This DAG runs daily at 4:00 AM to find photos from the same day across
multiple years in your local photo directory and copy them to a target
directory for use with Home Assistant. This solution avoids all cloud
sync and 2FA issues.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

# Import our local photos fetcher
from local_photos_fetcher import fetch_local_photos_airflow

# DAG configuration
DAG_ID = "local_photos_day_photos"
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
SOURCE_DIR = "/path/to/your/photo/library"  # Adjust this to your photo directory
OUTPUT_DIR = "/srv/homeassistant/media/day_photos"  # Adjust this path as needed
DATE_FORMAT = "YYYY-MM-DD"  # Adjust based on your filename format

# Create the DAG
dag = DAG(
    dag_id=DAG_ID,
    schedule_interval=SCHEDULE_INTERVAL,
    start_date=START_DATE,
    default_args=DEFAULT_ARGS,
    description="Fetch 'on this day' photos from local photo library",
    catchup=False,
    tags=["local", "photos", "homeassistant"],
)

# Task to fetch photos
fetch_photos_task = PythonOperator(
    task_id="fetch_local_photos",
    python_callable=fetch_local_photos_airflow,
    op_kwargs={
        "target_date": "{{ ds }}",  # Airflow template variable for execution date
        "years_back": YEARS_BACK,
        "source_dir": SOURCE_DIR,
        "output_dir": OUTPUT_DIR,
        "date_format": DATE_FORMAT,
    },
    dag=dag,
)

# Set task dependencies (if you add more tasks later)
fetch_photos_task

# Alternative configuration using Airflow Variables:
# If you prefer to use Airflow Variables for paths, replace the op_kwargs above with:
"""
fetch_photos_task = PythonOperator(
    task_id="fetch_local_photos",
    python_callable=fetch_local_photos_airflow,
    op_kwargs={
        "target_date": "{{ ds }}",
        "years_back": YEARS_BACK,
        "source_dir": "{{ var.value.LOCAL_PHOTOS_SOURCE_DIR }}",
        "output_dir": "{{ var.value.LOCAL_PHOTOS_OUTPUT_DIR }}",
        "date_format": "{{ var.value.LOCAL_PHOTOS_DATE_FORMAT }}",
    },
    dag=dag,
)
"""

# For manual testing, you can also create a simpler version:
"""
def create_simple_dag():
    '''Create a simpler DAG for testing'''
    simple_dag = DAG(
        dag_id="local_photos_simple",
        schedule_interval="0 4 * * *",
        start_date=datetime(2024, 1, 1),
        default_args=DEFAULT_ARGS,
        catchup=False,
    )
    
    PythonOperator(
        task_id="fetch_photos",
        python_callable=fetch_local_photos_airflow,
        op_kwargs={
            "target_date": "{{ ds }}",
            "years_back": 3,  # Shorter range for testing
            "source_dir": "/home/user/Photos",  # Replace with your path
            "output_dir": "./test_images",
            "date_format": "YYYY-MM-DD",
        },
        dag=simple_dag,
    )
    
    return simple_dag
""" 