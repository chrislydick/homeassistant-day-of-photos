#!/usr/bin/env python3
"""
Airflow DAG Loading Diagnostic Script

Run this on your Airflow machine to diagnose why DAGs aren't loading.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n🔍 {description}")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        return False

def check_airflow_status():
    """Check if Airflow is running."""
    print("=" * 60)
    print("🚀 AIRFLOW STATUS CHECK")
    print("=" * 60)
    
    # Check if Airflow processes are running
    run_command("ps aux | grep airflow | grep -v grep", "Airflow processes")
    
    # Check Airflow version
    run_command("airflow version", "Airflow version")
    
    # Check Airflow info
    run_command("airflow info", "Airflow info")

def check_airflow_config():
    """Check Airflow configuration."""
    print("\n" + "=" * 60)
    print("⚙️ AIRFLOW CONFIGURATION")
    print("=" * 60)
    
    # Check environment variables
    run_command("echo $AIRFLOW_HOME", "AIRFLOW_HOME")
    run_command("echo $DAGS_FOLDER", "DAGS_FOLDER")
    
    # Check airflow.cfg
    airflow_home = os.getenv('AIRFLOW_HOME', '~/.airflow')
    run_command(f"cat {airflow_home}/airflow.cfg | grep dags_folder", "DAGS_FOLDER from airflow.cfg")

def check_dags_directory():
    """Check the DAGs directory."""
    print("\n" + "=" * 60)
    print("📁 DAGS DIRECTORY CHECK")
    print("=" * 60)
    
    # Get DAGS_FOLDER
    dags_folder = os.getenv('DAGS_FOLDER', os.path.join(os.getenv('AIRFLOW_HOME', '~/.airflow'), 'dags'))
    
    # Check if directory exists
    run_command(f"ls -la {dags_folder}", "DAGS_FOLDER contents")
    
    # Check for Python files
    run_command(f"find {dags_folder} -name '*.py' -type f", "Python files in DAGS_FOLDER")

def test_dag_imports():
    """Test importing DAG files."""
    print("\n" + "=" * 60)
    print("🐍 DAG IMPORT TESTS")
    print("=" * 60)
    
    dags_folder = os.getenv('DAGS_FOLDER', os.path.join(os.getenv('AIRFLOW_HOME', '~/.airflow'), 'dags'))
    
    # Test simple DAG import
    run_command(f"cd {dags_folder} && python -c \"import simple_test_dag; print('✅ Simple test DAG imports successfully')\"", "Simple test DAG import")
    
    # Test OneDrive DAG import
    run_command(f"cd {dags_folder} && python -c \"import onedrive_photos_dag; print('✅ OneDrive DAG imports successfully')\"", "OneDrive DAG import")

def check_airflow_logs():
    """Check Airflow logs for errors."""
    print("\n" + "=" * 60)
    print("📋 AIRFLOW LOGS")
    print("=" * 60)
    
    airflow_home = os.getenv('AIRFLOW_HOME', '~/.airflow')
    
    # Check recent scheduler logs
    run_command(f"tail -20 {airflow_home}/logs/scheduler/*.log", "Recent scheduler logs")
    
    # Check for errors
    run_command(f"grep -i 'error\|exception\|traceback' {airflow_home}/logs/scheduler/*.log | tail -10", "Recent errors in scheduler logs")

def test_airflow_cli():
    """Test Airflow CLI commands."""
    print("\n" + "=" * 60)
    print("🛠️ AIRFLOW CLI TESTS")
    print("=" * 60)
    
    # List DAGs
    run_command("airflow dags list", "List all DAGs")
    
    # Test DAG parsing
    run_command("airflow dags test simple_test 2024-01-01", "Test simple DAG parsing")

def main():
    """Run all diagnostic checks."""
    print("🔧 AIRFLOW DAG LOADING DIAGNOSTIC")
    print("=" * 60)
    print("This script will help diagnose why DAGs aren't appearing in Airflow.")
    print("Run this on your Airflow machine.")
    print("=" * 60)
    
    check_airflow_status()
    check_airflow_config()
    check_dags_directory()
    test_dag_imports()
    check_airflow_logs()
    test_airflow_cli()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("Check the output above for any errors or issues.")
    print("Common issues:")
    print("- Import errors in DAG files")
    print("- Wrong DAGS_FOLDER configuration")
    print("- Missing dependencies")
    print("- Airflow services not running")
    print("- Database issues")

if __name__ == "__main__":
    main() 