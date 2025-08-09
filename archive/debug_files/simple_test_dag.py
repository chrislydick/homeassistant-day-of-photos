"""
Simple Test DAG for Airflow 2.10.2
"""

from datetime import datetime
from airflow import DAG

dag = DAG(
    dag_id="simple_test",
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 4 * * *",  # Use schedule_interval for 2.10.2
) 