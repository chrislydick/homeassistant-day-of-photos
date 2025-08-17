#!/usr/bin/env python3
"""
Setup script for iCloud Photos Airflow DAG

This script helps you:
1. Test iCloud authentication
2. Set up Airflow variables
3. Test the photo fetching functionality
"""

import os
import sys
from getpass import getpass
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from icloud_photo_fetcher import iCloudPhotoFetcher, fetch_photos_airflow
except ImportError as e:
    print(f"Error importing photo fetcher: {e}")
    print("Make sure you have installed the requirements: pip install -r requirements.txt")
    sys.exit(1)

try:
    from airflow.models import Variable
    from airflow import settings
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    print("Airflow not available - skipping Airflow variable setup")


def test_icloud_connection(username: str, password: str) -> bool:
    """Test iCloud connection and authentication."""
    print("Testing iCloud connection...")
    
    try:
        fetcher = iCloudPhotoFetcher(
            username=username,
            password=password,
            output_dir="./test_images"
        )
        
        if fetcher.authenticate():
            print("✅ iCloud authentication successful!")
            return True
        else:
            print("❌ iCloud authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing iCloud connection: {e}")
        return False


def test_photo_fetching(username: str, password: str, years_back: int = 2) -> bool:
    """Test photo fetching functionality."""
    print(f"Testing photo fetching (last {years_back} years)...")
    
    try:
        fetcher = iCloudPhotoFetcher(
            username=username,
            password=password,
            output_dir="./test_images"
        )
        
        downloaded_files = fetcher.fetch_and_download(
            years_back=years_back,
            skip_existing=False
        )
        
        print(f"✅ Successfully downloaded {len(downloaded_files)} photos!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing photo fetching: {e}")
        return False


def setup_airflow_variables(username: str, password: str) -> bool:
    """Set up Airflow variables for iCloud credentials."""
    if not AIRFLOW_AVAILABLE:
        print("⚠️  Airflow not available - skipping variable setup")
        return False
    
    print("Setting up Airflow variables...")
    
    try:
        # Initialize Airflow session
        session = settings.Session()
        
        # Set username variable
        username_var = Variable.get("ICLOUD_USERNAME", default_var=None)
        if username_var is None:
            Variable.set("ICLOUD_USERNAME", username)
            print("✅ Set ICLOUD_USERNAME variable")
        else:
            print("⚠️  ICLOUD_USERNAME variable already exists")
        
        # Set password variable
        password_var = Variable.get("ICLOUD_PASSWORD", default_var=None)
        if password_var is None:
            Variable.set("ICLOUD_PASSWORD", password)
            print("✅ Set ICLOUD_PASSWORD variable")
        else:
            print("⚠️  ICLOUD_PASSWORD variable already exists")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Airflow variables: {e}")
        return False


def main():
    """Main setup function."""
    print("=== iCloud Photos Airflow Setup ===\n")
    
    # Get credentials
    print("Please provide your iCloud credentials:")
    username = input("Apple ID (email): ").strip()
    password = getpass("App-specific password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required!")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Test iCloud connection
    if not test_icloud_connection(username, password):
        print("\n❌ Setup failed - iCloud connection test failed!")
        print("Please check your credentials and try again.")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Test photo fetching
    years_back = input("How many years back to test? (default: 2): ").strip()
    years_back = int(years_back) if years_back.isdigit() else 2
    
    if not test_photo_fetching(username, password, years_back):
        print("\n❌ Setup failed - photo fetching test failed!")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Setup Airflow variables
    setup_airflow = input("Set up Airflow variables? (y/n): ").strip().lower()
    if setup_airflow == 'y':
        setup_airflow_variables(username, password)
    
    print("\n" + "="*50)
    
    # Final instructions
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy icloud_photos_dag.py to your Airflow dags/ folder")
    print("2. Ensure the output directory exists and is writable")
    print("3. Restart Airflow webserver and scheduler")
    print("4. The DAG will run daily at 4:00 AM")
    print("\nFor 2FA issues:")
    print("- Set ICLOUD_2FA_CODE environment variable with your verification code")
    print("- Set ICLOUD_2FA_DEVICE environment variable if you have multiple devices")
    print("- The session will be saved for future runs")


if __name__ == "__main__":
    main() 