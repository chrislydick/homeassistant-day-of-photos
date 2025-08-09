"""
Ultimate Airflow Test DAG - The Simplest Possible DAG
"""

from datetime import datetime
from airflow import DAG

# The absolute minimum DAG definition
dag = DAG(
    dag_id="ultimate_test",
    start_date=datetime(2024, 1, 1),
) 