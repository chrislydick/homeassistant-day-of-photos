#!/usr/bin/env python3
"""
Setup script for Google Photos Airflow DAG

This script helps you:
1. Test Google Photos authentication
2. Set up OAuth credentials
3. Test the photo fetching functionality
4. Configure Airflow variables (optional)
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from google_photos_fetcher import GooglePhotosFetcher, fetch_google_photos_airflow
except ImportError as e:
    print(f"Error importing Google Photos fetcher: {e}")
    print("Make sure you have installed the requirements: pip install -r requirements.txt")
    sys.exit(1)

try:
    from airflow.models import Variable
    from airflow import settings
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    print("Airflow not available - skipping Airflow variable setup")


def check_credentials_file() -> bool:
    """Check if credentials file exists and is valid."""
    creds_file = Path("creds.json")
    
    if not creds_file.exists():
        print("❌ Credentials file 'creds.json' not found!")
        print("\nTo get your credentials file:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable the Google Photos Library API")
        print("4. Go to 'Credentials' and create OAuth 2.0 Client ID")
        print("5. Download the JSON file and save it as 'creds.json'")
        return False
    
    try:
        import json
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' in creds_data and 'client_id' in creds_data['installed']:
            print("✅ Credentials file looks valid")
            return True
        else:
            print("❌ Credentials file format appears invalid")
            return False
            
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False


def test_google_photos_connection() -> bool:
    """Test Google Photos connection and authentication."""
    print("Testing Google Photos connection...")
    
    try:
        fetcher = GooglePhotosFetcher(
            credentials_file="creds.json",
            token_file="token.pickle",
            output_dir="./test_images"
        )
        
        if fetcher.authenticate():
            print("✅ Google Photos authentication successful!")
            return True
        else:
            print("❌ Google Photos authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Photos connection: {e}")
        return False


def test_photo_fetching(years_back: int = 2) -> bool:
    """Test photo fetching functionality."""
    print(f"Testing photo fetching (last {years_back} years)...")
    
    try:
        fetcher = GooglePhotosFetcher(
            credentials_file="creds.json",
            token_file="token.pickle",
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


def setup_airflow_variables() -> bool:
    """Set up Airflow variables for Google Photos configuration."""
    if not AIRFLOW_AVAILABLE:
        print("⚠️  Airflow not available - skipping variable setup")
        return False
    
    print("Setting up Airflow variables...")
    
    try:
        # Initialize Airflow session
        session = settings.Session()
        
        # Set output directory variable
        output_dir_var = Variable.get("GOOGLE_PHOTOS_OUTPUT_DIR", default_var=None)
        if output_dir_var is None:
            Variable.set("GOOGLE_PHOTOS_OUTPUT_DIR", "/srv/homeassistant/media/day_photos")
            print("✅ Set GOOGLE_PHOTOS_OUTPUT_DIR variable")
        else:
            print("⚠️  GOOGLE_PHOTOS_OUTPUT_DIR variable already exists")
        
        # Set credentials file path variable
        creds_file_var = Variable.get("GOOGLE_PHOTOS_CREDENTIALS_FILE", default_var=None)
        if creds_file_var is None:
            Variable.set("GOOGLE_PHOTOS_CREDENTIALS_FILE", "/opt/airflow/dags/creds.json")
            print("✅ Set GOOGLE_PHOTOS_CREDENTIALS_FILE variable")
        else:
            print("⚠️  GOOGLE_PHOTOS_CREDENTIALS_FILE variable already exists")
        
        # Set token file path variable
        token_file_var = Variable.get("GOOGLE_PHOTOS_TOKEN_FILE", default_var=None)
        if token_file_var is None:
            Variable.set("GOOGLE_PHOTOS_TOKEN_FILE", "/opt/airflow/dags/token.pickle")
            print("✅ Set GOOGLE_PHOTOS_TOKEN_FILE variable")
        else:
            print("⚠️  GOOGLE_PHOTOS_TOKEN_FILE variable already exists")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Airflow variables: {e}")
        return False


def main():
    """Main setup function."""
    print("=== Google Photos Airflow Setup ===\n")
    
    print("This setup will help you configure Google Photos for Airflow.")
    print("Note: This solution avoids the 2FA issues common with iCloud.\n")
    
    print("="*50)
    
    # Check credentials file
    if not check_credentials_file():
        print("\n❌ Setup failed - credentials file not found or invalid!")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Test Google Photos connection
    if not test_google_photos_connection():
        print("\n❌ Setup failed - Google Photos connection test failed!")
        print("Please check your credentials and try again.")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Test photo fetching
    years_back = input("How many years back to test? (default: 2): ").strip()
    years_back = int(years_back) if years_back.isdigit() else 2
    
    if not test_photo_fetching(years_back):
        print("\n❌ Setup failed - photo fetching test failed!")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Setup Airflow variables
    setup_airflow = input("Set up Airflow variables? (y/n): ").strip().lower()
    if setup_airflow == 'y':
        setup_airflow_variables()
    
    print("\n" + "="*50)
    
    # Final instructions
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy google_photos_dag.py to your Airflow dags/ folder")
    print("2. Copy creds.json and token.pickle to your Airflow dags/ folder")
    print("3. Ensure the output directory exists and is writable")
    print("4. Restart Airflow webserver and scheduler")
    print("5. The DAG will run daily at 4:00 AM")
    print("\nAdvantages over iCloud:")
    print("- No 2FA issues or device trust problems")
    print("- More reliable OAuth authentication")
    print("- Better API stability and documentation")
    print("- Automatic token refresh")


if __name__ == "__main__":
    main() 