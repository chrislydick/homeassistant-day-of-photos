"""
OneDrive Photos DAG for Airflow 2.10.2

This DAG fetches photos from OneDrive for a specific date across multiple years.
It's designed to work with photos synced from iCloud to OneDrive.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from onedrive_photos_fetcher import fetch_onedrive_photos_airflow
import subprocess
import os
import shutil

# DAG Configuration
DAG_ID = "onedrive_day_photos"
SCHEDULE_INTERVAL = "0 4 * * *"  # Run at 4:00 AM daily
START_DATE = datetime(2024, 1, 1)

# Home Assistant Server Configuration - These will be loaded from Airflow Variables
# HOMEASSISTANT_HOST, HOMEASSISTANT_USER, HOMEASSISTANT_PHOTOS_DIR

def transfer_photos_to_homeassistant(local_dir, remote_host, remote_user, remote_dir, ssh_port="22"):
    """Transfer photos from Airflow server to Home Assistant server via SCP"""
    try:
        # Create remote directory if it doesn't exist
        ssh_cmd = f"ssh -p {ssh_port} {remote_user}@{remote_host} 'mkdir -p {remote_dir}'"
        subprocess.run(ssh_cmd, shell=True, check=True)
        
        # Transfer files
        scp_cmd = f"scp -P {ssh_port} -r {local_dir}/* {remote_user}@{remote_host}:{remote_dir}/"
        result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully transferred photos to {remote_host}:{remote_dir}")
            return True
        else:
            print(f"❌ Failed to transfer photos: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error transferring photos: {e}")
        return False

def fetch_photos_function(**context):
    """Fetch photos from OneDrive for this day in history."""
    from airflow.models import Variable
    
    # Get OneDrive credentials from Airflow variables
    client_id = Variable.get("ONEDRIVE_CLIENT_ID", default_var=None)
    client_secret = Variable.get("ONEDRIVE_CLIENT_SECRET", default_var=None)
    
    if not client_id or not client_secret:
        raise ValueError("ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET must be set in Airflow Variables")
    
    # Get Home Assistant server configuration from Airflow variables
    homeassistant_host = Variable.get("HOMEASSISTANT_HOST", default_var=None)
    homeassistant_user = Variable.get("HOMEASSISTANT_USER", default_var=None)
    homeassistant_photos_dir = Variable.get("HOMEASSISTANT_PHOTOS_DIR", default_var=None)
    homeassistant_ssh_port = Variable.get("HOMEASSISTANT_SSH_PORT", default_var="22")
    
    if not homeassistant_host or not homeassistant_user or not homeassistant_photos_dir:
        raise ValueError("HOMEASSISTANT_HOST, HOMEASSISTANT_USER, and HOMEASSISTANT_PHOTOS_DIR must be set in Airflow Variables")
    
    # Local temporary directory on Airflow server
    local_temp_dir = "/tmp/onedrive_photos_temp"
    
    # Call the fetcher function to download photos locally
    fetch_onedrive_photos_airflow(
        target_date=None,  # Use today's date
        years_back=5,
        output_dir=local_temp_dir,
        client_id=client_id,
        client_secret=client_secret,
        token_file="/home/chrislydick/airflow/dags/onedrive_token.pickle",
        photos_folder="Pictures"
    )
    
    # Transfer photos to Home Assistant server
    if os.path.exists(local_temp_dir) and os.listdir(local_temp_dir):
        transfer_success = transfer_photos_to_homeassistant(
            local_temp_dir,
            homeassistant_host,
            homeassistant_user,
            homeassistant_photos_dir,
            homeassistant_ssh_port
        )
        
        if transfer_success:
            # Clean up local temporary files
            shutil.rmtree(local_temp_dir, ignore_errors=True)
            print("✅ Cleaned up local temporary files")
        else:
            print("⚠️  Transfer failed, keeping local files for debugging")
    else:
        print("ℹ️  No photos downloaded, skipping transfer")
    
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