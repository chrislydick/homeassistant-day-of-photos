#!/usr/bin/env python3
"""
OneDrive Photos Setup Script

This script helps you set up OneDrive photo fetching, including
instructions for syncing photos from iCloud to OneDrive.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from onedrive_photos_fetcher import OneDrivePhotosFetcher

def print_header():
    print("=" * 60)
    print("OneDrive Photos Setup")
    print("=" * 60)
    print()

def print_icloud_sync_instructions():
    print("📱 STEP 1: Sync iCloud Photos to OneDrive")
    print("-" * 40)
    print()
    print("Since you're on Linux, here are your options to sync iCloud → OneDrive:")
    print()
    
    print("🔹 Option A: Windows/Mac Machine (Recommended)")
    print("   1. On a Windows/Mac machine with iCloud access:")
    print("      - Install iCloud Desktop app")
    print("      - Install OneDrive Desktop app")
    print("      - Configure OneDrive to sync iCloud Photos folder")
    print("      - Photos will automatically sync to OneDrive")
    print()
    
    print("🔹 Option B: Cloud-to-Cloud Sync Service")
    print("   1. Use Mover.io (Microsoft-owned, free):")
    print("      - Go to https://mover.io")
    print("      - Connect iCloud account")
    print("      - Connect OneDrive account")
    print("      - Set up automatic sync from iCloud Photos → OneDrive")
    print()
    
    print("🔹 Option C: Manual Sync")
    print("   1. Download photos from iCloud web interface")
    print("   2. Upload to OneDrive web interface")
    print("   3. Repeat periodically")
    print()
    
    input("Press Enter when you have photos synced to OneDrive...")

def setup_onedrive_app():
    print("🔧 STEP 2: Create OneDrive App")
    print("-" * 40)
    print()
    print("1. Go to Azure Portal: https://portal.azure.com")
    print("2. Sign in with your Microsoft account")
    print("3. Go to 'Azure Active Directory' → 'App registrations'")
    print("4. Click 'New registration'")
    print("5. Fill in the details:")
    print("   - Name: 'Photo Fetcher'")
    print("   - Supported account types: 'Personal Microsoft accounts only'")
    print("   - Redirect URI: 'http://localhost:8080' (Web)")
    print("6. Click 'Register'")
    print("7. Note down the 'Application (client) ID'")
    print("8. Go to 'Certificates & secrets' → 'New client secret'")
    print("9. Add a description and choose expiration")
    print("10. Copy the secret value (you won't see it again)")
    print()
    
    # Check for environment variables first
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if client_id and client_secret:
        print("✅ Found credentials in environment variables!")
        print(f"Client ID: {client_id[:8]}...")
        print(f"Client Secret: {client_secret[:8]}...")
        use_env = input("Use these credentials? (y/n): ").strip().lower()
        
        if use_env == 'y':
            return client_id, client_secret
    
    print("Enter your credentials:")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    return client_id, client_secret

def test_onedrive_connection(client_id, client_secret):
    print("🧪 STEP 3: Test OneDrive Connection")
    print("-" * 40)
    print()
    
    try:
        # Use environment variables if credentials are None
        if not client_id or not client_secret:
            import os
            client_id = client_id or os.getenv("ONEDRIVE_CLIENT_ID")
            client_secret = client_secret or os.getenv("ONEDRIVE_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                print("❌ No credentials provided. Set ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET environment variables or provide them as parameters.")
                return False
        
        fetcher = OneDrivePhotosFetcher(
            client_id=client_id,
            client_secret=client_secret,
            token_file="./onedrive_token.pickle",
            output_dir="./test_images",
            photos_folder="Pictures"
        )
        
        print("Testing authentication...")
        if fetcher.authenticate():
            print("✅ Authentication successful!")
            
            # Test photo search
            print("Testing photo search...")
            photos_data = fetcher.search_photos_for_date(
                target_date=datetime.now(),
                years_back=1
            )
            
            print(f"✅ Found {len(photos_data)} photos in OneDrive")
            
            if photos_data:
                print("Testing photo download...")
                downloaded = fetcher.download_photos(photos_data[:2])  # Download first 2 photos
                print(f"✅ Downloaded {len(downloaded)} test photos")
            
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_airflow_variables(client_id, client_secret):
    print("⚙️ STEP 4: Airflow Variables Setup")
    print("-" * 40)
    print()
    print("You need to set these variables in Airflow:")
    print()
    print("Variable Name: ONEDRIVE_CLIENT_ID")
    print(f"Variable Value: {client_id}")
    print()
    print("Variable Name: ONEDRIVE_CLIENT_SECRET")
    print(f"Variable Value: {client_secret}")
    print()
    
    setup_airflow = input("Would you like to set up Airflow variables automatically? (y/n): ").strip().lower()
    
    if setup_airflow == 'y':
        try:
            from airflow.models import Variable
            Variable.set("ONEDRIVE_CLIENT_ID", client_id)
            Variable.set("ONEDRIVE_CLIENT_SECRET", client_secret)
            print("✅ Airflow variables set successfully!")
        except Exception as e:
            print(f"❌ Failed to set Airflow variables: {e}")
            print("Please set them manually in the Airflow UI")
    else:
        print("Please set the variables manually in the Airflow UI")

def print_deployment_instructions():
    print("🚀 STEP 5: Deploy to Airflow")
    print("-" * 40)
    print()
    print("1. Copy the OneDrive files to your Airflow dags folder:")
    print("   cp onedrive_photos_fetcher.py /path/to/airflow/dags/")
    print("   cp onedrive_photos_dag.py /path/to/airflow/dags/")
    print()
    print("2. Copy the token file to your Airflow dags folder:")
    print("   cp onedrive_token.pickle /opt/airflow/dags/")
    print("3. Update the DAG configuration if needed:")
    print("   - Edit OUTPUT_DIR in onedrive_photos_dag.py")
    print("   - Update PHOTOS_FOLDER if needed")
    print()
    print("3. Restart Airflow services")
    print("4. The DAG will run daily at 4:00 AM")
    print()

def main():
    print_header()
    
    # Step 1: iCloud sync instructions
    print_icloud_sync_instructions()
    
    # Step 2: OneDrive app setup
    client_id, client_secret = setup_onedrive_app()
    
    # Step 3: Test connection
    if test_onedrive_connection(client_id, client_secret):
        print("✅ OneDrive setup successful!")
        
        # Step 4: Airflow variables
        setup_airflow_variables(client_id, client_secret)
        
        # Step 5: Deployment instructions
        print_deployment_instructions()
        
        print("🎉 Setup complete! Your OneDrive photo fetcher is ready.")
    else:
        print("❌ Setup failed. Please check your configuration and try again.")

if __name__ == "__main__":
    from datetime import datetime
    main() 