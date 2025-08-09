#!/usr/bin/env python3
"""
Airflow DAG Loading Diagnostic Script

This script will help identify why DAGs aren't showing up in your Airflow instance.
Run this on your Airflow machine.
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n🔍 {description}")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        print(f"Exception: {e}")
        return False, ""

def check_airflow_basics():
    """Check basic Airflow setup."""
    print("=" * 60)
    print("🚀 BASIC AIRFLOW SETUP")
    print("=" * 60)
    
    # Check if Airflow is installed
    success, output = run_command("which airflow", "Airflow installation location")
    
    # Check Airflow version
    run_command("airflow version", "Airflow version")
    
    # Check if Airflow processes are running
    run_command("ps aux | grep airflow | grep -v grep", "Running Airflow processes")
    
    # Check Airflow info
    run_command("airflow info", "Airflow configuration info")

def check_environment_variables():
    """Check environment variables."""
    print("\n" + "=" * 60)
    print("⚙️ ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    # Check key environment variables
    run_command("echo $AIRFLOW_HOME", "AIRFLOW_HOME")
    run_command("echo $DAGS_FOLDER", "DAGS_FOLDER")
    run_command("echo $PYTHONPATH", "PYTHONPATH")
    
    # Check if DAGS_FOLDER is set in Airflow
    run_command("airflow info | grep -i dags", "DAGS_FOLDER from Airflow")

def check_dags_directory():
    """Check DAGs directory."""
    print("\n" + "=" * 60)
    print("📁 DAGS DIRECTORY CHECK")
    print("=" * 60)
    
    # Get DAGS_FOLDER from environment or Airflow
    success, dags_folder = run_command("airflow info | grep 'DAGS_FOLDER' | awk '{print $2}'", "Get DAGS_FOLDER from Airflow")
    
    if not dags_folder:
        # Try common locations
        common_locations = [
            "/opt/airflow/dags",
            "~/.airflow/dags", 
            "/usr/local/airflow/dags",
            "/var/lib/airflow/dags"
        ]
        
        for location in common_locations:
            expanded_location = os.path.expanduser(location)
            if os.path.exists(expanded_location):
                dags_folder = expanded_location
                print(f"Found DAGS_FOLDER at: {dags_folder}")
                break
    
    if dags_folder:
        print(f"Using DAGS_FOLDER: {dags_folder}")
        
        # Check if directory exists
        run_command(f"ls -la {dags_folder}", f"Contents of {dags_folder}")
        
        # Check for Python files
        run_command(f"find {dags_folder} -name '*.py' -type f", "Python files in DAGS_FOLDER")
        
        # Check file permissions
        run_command(f"ls -la {dags_folder}/*.py", "File permissions")
        
        return dags_folder
    else:
        print("❌ No DAGS_FOLDER found!")
        return None

def test_dag_imports(dags_folder):
    """Test importing DAG files."""
    print("\n" + "=" * 60)
    print("🐍 DAG IMPORT TESTS")
    print("=" * 60)
    
    if not dags_folder:
        print("❌ No DAGS_FOLDER available for import tests")
        return
    
    # Find Python files in DAGS_FOLDER
    success, output = run_command(f"find {dags_folder} -name '*.py' -type f", "Find Python files")
    
    if success and output:
        python_files = output.strip().split('\n')
        
        for py_file in python_files:
            if py_file:
                filename = os.path.basename(py_file)
                module_name = os.path.splitext(filename)[0]
                
                print(f"\nTesting import of: {filename}")
                
                # Test basic Python import
                test_cmd = f"cd {dags_folder} && python -c \"import {module_name}; print('✅ {module_name} imports successfully')\""
                run_command(test_cmd, f"Import test for {module_name}")
                
                # Test Airflow DAG import
                test_cmd = f"cd {dags_folder} && python -c \"from airflow import DAG; import {module_name}; print('✅ {module_name} DAG imports successfully')\""
                run_command(test_cmd, f"Airflow DAG import test for {module_name}")

def check_airflow_cli():
    """Check Airflow CLI commands."""
    print("\n" + "=" * 60)
    print("🛠️ AIRFLOW CLI TESTS")
    print("=" * 60)
    
    # List DAGs
    run_command("airflow dags list", "List all DAGs")
    
    # Check DAG parsing
    run_command("airflow dags test ultimate_test 2024-01-01", "Test ultimate_test DAG parsing")
    run_command("airflow dags test simple_test 2024-01-01", "Test simple_test DAG parsing")
    run_command("airflow dags test onedrive_day_photos 2024-01-01", "Test onedrive_day_photos DAG parsing")

def check_airflow_logs():
    """Check Airflow logs for errors."""
    print("\n" + "=" * 60)
    print("📋 AIRFLOW LOGS")
    print("=" * 60)
    
    # Find Airflow home
    success, airflow_home = run_command("airflow info | grep 'AIRFLOW_HOME' | awk '{print $2}'", "Get AIRFLOW_HOME")
    
    if success and airflow_home:
        # Check recent scheduler logs
        run_command(f"tail -20 {airflow_home}/logs/scheduler/*.log", "Recent scheduler logs")
        
        # Check for errors
        run_command(f"grep -i 'error\|exception\|traceback' {airflow_home}/logs/scheduler/*.log | tail -10", "Recent errors in scheduler logs")
        
        # Check webserver logs
        run_command(f"tail -20 {airflow_home}/logs/webserver/*.log", "Recent webserver logs")
    else:
        print("❌ Could not find AIRFLOW_HOME for log checking")

def check_systemd_services():
    """Check systemd services if applicable."""
    print("\n" + "=" * 60)
    print("🔧 SYSTEMD SERVICES")
    print("=" * 60)
    
    # Check if Airflow services are running via systemctl
    run_command("systemctl list-units --type=service | grep airflow", "Airflow systemd services")
    
    # Check service status
    run_command("systemctl status airflow-webserver", "Airflow webserver service status")
    run_command("systemctl status airflow-scheduler", "Airflow scheduler service status")
    
    # Check service environment
    run_command("systemctl show airflow-webserver | grep Environment", "Airflow webserver environment")

def create_test_dag(dags_folder):
    """Create a minimal test DAG."""
    print("\n" + "=" * 60)
    print("🧪 CREATING TEST DAG")
    print("=" * 60)
    
    if not dags_folder:
        print("❌ No DAGS_FOLDER available for test DAG creation")
        return
    
    test_dag_content = '''"""
Minimal Test DAG for Airflow
"""

from datetime import datetime
from airflow import DAG

dag = DAG(
    dag_id="minimal_test",
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 4 * * *",
)
'''
    
    test_dag_path = os.path.join(dags_folder, "minimal_test_dag.py")
    
    try:
        with open(test_dag_path, 'w') as f:
            f.write(test_dag_content)
        
        print(f"✅ Created test DAG at: {test_dag_path}")
        
        # Test the new DAG
        run_command(f"cd {dags_folder} && python -c \"import minimal_test_dag; print('✅ Test DAG imports successfully')\"", "Test new DAG import")
        
        # Check if it appears in Airflow
        run_command("airflow dags list | grep minimal_test", "Check if test DAG appears in list")
        
    except Exception as e:
        print(f"❌ Failed to create test DAG: {e}")

def main():
    """Run all diagnostic checks."""
    print("🔧 AIRFLOW DAG LOADING DIAGNOSTIC")
    print("=" * 60)
    print("This script will help identify why DAGs aren't appearing in Airflow.")
    print("Run this on your Airflow machine.")
    print("=" * 60)
    
    # Run all checks
    check_airflow_basics()
    check_environment_variables()
    dags_folder = check_dags_directory()
    test_dag_imports(dags_folder)
    check_airflow_cli()
    check_airflow_logs()
    check_systemd_services()
    create_test_dag(dags_folder)
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("Check the output above for any errors or issues.")
    print("\nCommon issues found:")
    print("- DAGS_FOLDER not set or incorrect")
    print("- File permissions issues")
    print("- Import errors in DAG files")
    print("- Airflow services not running")
    print("- Systemd configuration issues")
    print("- Missing dependencies")

if __name__ == "__main__":
    main() 