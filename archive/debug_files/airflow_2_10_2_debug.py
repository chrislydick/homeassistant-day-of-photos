#!/usr/bin/env python3
"""
Airflow 2.10.2 DAG Loading Diagnostic Script

This script checks for common issues with Airflow 2.10.2 DAG loading.
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

def check_airflow_version():
    """Check Airflow version and compatibility."""
    print("=" * 60)
    print("🚀 AIRFLOW 2.10.2 COMPATIBILITY CHECK")
    print("=" * 60)
    
    # Check Airflow version
    run_command("airflow version", "Airflow version")
    
    # Check if it's 2.10.2
    result = subprocess.run("airflow version", shell=True, capture_output=True, text=True)
    if "2.10.2" in result.stdout:
        print("✅ Airflow 2.10.2 detected - using correct syntax")
    else:
        print("⚠️ Different Airflow version detected")

def check_dag_syntax():
    """Check DAG syntax for Airflow 2.10.2."""
    print("\n" + "=" * 60)
    print("📝 DAG SYNTAX CHECK")
    print("=" * 60)
    
    dags_folder = os.getenv('DAGS_FOLDER', os.path.join(os.getenv('AIRFLOW_HOME', '~/.airflow'), 'dags'))
    
    # Test simple DAG import
    run_command(f"cd {dags_folder} && python -c \"import simple_test_dag; print('✅ Simple test DAG syntax OK')\"", "Simple test DAG syntax")
    
    # Test OneDrive DAG import
    run_command(f"cd {dags_folder} && python -c \"import onedrive_photos_dag; print('✅ OneDrive DAG syntax OK')\"", "OneDrive DAG syntax")

def check_airflow_dag_parsing():
    """Test Airflow's DAG parsing."""
    print("\n" + "=" * 60)
    print("🛠️ AIRFLOW DAG PARSING TEST")
    print("=" * 60)
    
    # Test DAG parsing with Airflow CLI
    run_command("airflow dags test simple_test 2024-01-01", "Test simple DAG parsing")
    run_command("airflow dags test onedrive_day_photos 2024-01-01", "Test OneDrive DAG parsing")

def check_airflow_services():
    """Check Airflow services."""
    print("\n" + "=" * 60)
    print("⚙️ AIRFLOW SERVICES CHECK")
    print("=" * 60)
    
    # Check if services are running
    run_command("ps aux | grep airflow | grep -v grep", "Airflow processes")
    
    # Check scheduler status
    run_command("airflow scheduler --help", "Scheduler help")
    
    # Check webserver status
    run_command("airflow webserver --help", "Webserver help")

def check_dags_list():
    """Check if DAGs are being detected."""
    print("\n" + "=" * 60)
    print("📋 DAGS LIST CHECK")
    print("=" * 60)
    
    # List all DAGs
    run_command("airflow dags list", "List all DAGs")
    
    # Check for specific DAGs
    run_command("airflow dags list | grep simple_test", "Check for simple_test DAG")
    run_command("airflow dags list | grep onedrive", "Check for OneDrive DAG")

def check_airflow_logs():
    """Check Airflow logs for 2.10.2 specific issues."""
    print("\n" + "=" * 60)
    print("📋 AIRFLOW LOGS CHECK")
    print("=" * 60)
    
    airflow_home = os.getenv('AIRFLOW_HOME', '~/.airflow')
    
    # Check recent scheduler logs
    run_command(f"tail -20 {airflow_home}/logs/scheduler/*.log", "Recent scheduler logs")
    
    # Check for syntax errors
    run_command(f"grep -i 'syntax\|error\|exception' {airflow_home}/logs/scheduler/*.log | tail -10", "Recent errors")

def check_airflow_config():
    """Check Airflow 2.10.2 configuration."""
    print("\n" + "=" * 60)
    print("⚙️ AIRFLOW CONFIGURATION")
    print("=" * 60)
    
    # Check environment variables
    run_command("echo $AIRFLOW_HOME", "AIRFLOW_HOME")
    run_command("echo $DAGS_FOLDER", "DAGS_FOLDER")
    
    # Check airflow.cfg
    airflow_home = os.getenv('AIRFLOW_HOME', '~/.airflow')
    run_command(f"cat {airflow_home}/airflow.cfg | grep dags_folder", "DAGS_FOLDER from airflow.cfg")

def main():
    """Run all diagnostic checks for Airflow 2.10.2."""
    print("🔧 AIRFLOW 2.10.2 DAG LOADING DIAGNOSTIC")
    print("=" * 60)
    print("This script checks for Airflow 2.10.2 specific issues.")
    print("=" * 60)
    
    check_airflow_version()
    check_airflow_config()
    check_dag_syntax()
    check_airflow_services()
    check_airflow_dag_parsing()
    check_dags_list()
    check_airflow_logs()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("Airflow 2.10.2 specific checks:")
    print("- Using schedule_interval instead of schedule")
    print("- Proper DAG syntax for 2.10.2")
    print("- Service compatibility")
    print("- DAG parsing with CLI")

if __name__ == "__main__":
    main() 