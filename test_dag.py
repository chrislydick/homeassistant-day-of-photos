"""
Test DAG to verify Airflow setup
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def test_function():
    print("Test DAG is working!")
    return "Success"

# Create a simple test DAG
dag = DAG(
    dag_id="test_dag",
    description="Simple test DAG",
    schedule="0 4 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["test"],
)

test_task = PythonOperator(
    task_id="test_task",
    python_callable=test_function,
    dag=dag,
)

test_task 