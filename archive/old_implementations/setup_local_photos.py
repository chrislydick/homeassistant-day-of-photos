#!/usr/bin/env python3
"""
Setup script for Local Photos Airflow DAG

This script helps you:
1. Test local photo directory access
2. Configure photo directory paths
3. Test the photo finding and copying functionality
4. Configure Airflow variables (optional)
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from local_photos_fetcher import LocalPhotosFetcher, fetch_local_photos_airflow
except ImportError as e:
    print(f"Error importing local photos fetcher: {e}")
    print("Make sure you have installed the requirements: pip install -r requirements.txt")
    sys.exit(1)

try:
    from airflow.models import Variable
    from airflow import settings
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    print("Airflow not available - skipping Airflow variable setup")


def check_photo_directory(directory_path: str) -> bool:
    """Check if photo directory exists and contains photos."""
    photo_dir = Path(directory_path)
    
    if not photo_dir.exists():
        print(f"❌ Directory does not exist: {directory_path}")
        return False
    
    if not photo_dir.is_dir():
        print(f"❌ Path is not a directory: {directory_path}")
        return False
    
    # Check for photo files
    photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef']
    photo_files = []
    
    for ext in photo_extensions:
        photo_files.extend(photo_dir.rglob(f"*{ext}"))
        photo_files.extend(photo_dir.rglob(f"*{ext.upper()}"))
    
    if not photo_files:
        print(f"❌ No photo files found in directory: {directory_path}")
        print("Supported formats: jpg, jpeg, png, gif, bmp, tiff, heic, heif, webp, raw, cr2, nef")
        return False
    
    print(f"✅ Found {len(photo_files)} photo files in directory")
    return True


def test_photo_finding(source_dir: str, years_back: int = 2) -> bool:
    """Test photo finding functionality."""
    print(f"Testing photo finding (last {years_back} years)...")
    
    try:
        fetcher = LocalPhotosFetcher(
            source_dir=source_dir,
            output_dir="./test_images"
        )
        
        copied_files = fetcher.fetch_and_copy(
            years_back=years_back,
            skip_existing=False
        )
        
        print(f"✅ Successfully found and copied {len(copied_files)} photos!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing photo finding: {e}")
        return False


def setup_airflow_variables(source_dir: str, output_dir: str, date_format: str) -> bool:
    """Set up Airflow variables for local photos configuration."""
    if not AIRFLOW_AVAILABLE:
        print("⚠️  Airflow not available - skipping variable setup")
        return False
    
    print("Setting up Airflow variables...")
    
    try:
        # Initialize Airflow session
        session = settings.Session()
        
        # Set source directory variable
        source_dir_var = Variable.get("LOCAL_PHOTOS_SOURCE_DIR", default_var=None)
        if source_dir_var is None:
            Variable.set("LOCAL_PHOTOS_SOURCE_DIR", source_dir)
            print("✅ Set LOCAL_PHOTOS_SOURCE_DIR variable")
        else:
            print("⚠️  LOCAL_PHOTOS_SOURCE_DIR variable already exists")
        
        # Set output directory variable
        output_dir_var = Variable.get("LOCAL_PHOTOS_OUTPUT_DIR", default_var=None)
        if output_dir_var is None:
            Variable.set("LOCAL_PHOTOS_OUTPUT_DIR", output_dir)
            print("✅ Set LOCAL_PHOTOS_OUTPUT_DIR variable")
        else:
            print("⚠️  LOCAL_PHOTOS_OUTPUT_DIR variable already exists")
        
        # Set date format variable
        date_format_var = Variable.get("LOCAL_PHOTOS_DATE_FORMAT", default_var=None)
        if date_format_var is None:
            Variable.set("LOCAL_PHOTOS_DATE_FORMAT", date_format)
            print("✅ Set LOCAL_PHOTOS_DATE_FORMAT variable")
        else:
            print("⚠️  LOCAL_PHOTOS_DATE_FORMAT variable already exists")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Airflow variables: {e}")
        return False


def suggest_photo_directories() -> list:
    """Suggest common photo directory locations."""
    suggestions = []
    
    # Common photo directory locations
    common_paths = [
        "~/Pictures",
        "~/Photos", 
        "~/Desktop/Photos",
        "~/Documents/Photos",
        "/Users/*/Pictures",
        "/Users/*/Photos",
        "/home/*/Pictures",
        "/home/*/Photos",
        "/media/*/Photos",
        "/mnt/*/Photos"
    ]
    
    for path in common_paths:
        expanded_path = os.path.expanduser(path)
        if "*" in expanded_path:
            # Handle wildcard paths
            import glob
            matches = glob.glob(expanded_path)
            suggestions.extend(matches)
        elif os.path.exists(expanded_path):
            suggestions.append(expanded_path)
    
    return suggestions


def main():
    """Main setup function."""
    print("=== Local Photos Airflow Setup ===\n")
    
    print("This setup will help you configure local photos for Airflow.")
    print("This solution avoids all cloud sync and 2FA issues.\n")
    
    print("="*50)
    
    # Get source directory
    print("Please provide your photo directory path:")
    print("\nCommon locations:")
    suggestions = suggest_photo_directories()
    for i, suggestion in enumerate(suggestions[:5], 1):  # Show first 5 suggestions
        print(f"  {i}. {suggestion}")
    
    source_dir = input("\nEnter photo directory path: ").strip()
    
    if not source_dir:
        print("❌ Source directory is required!")
        sys.exit(1)
    
    # Check source directory
    if not check_photo_directory(source_dir):
        print("\n❌ Setup failed - photo directory check failed!")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Get output directory
    output_dir = input("Enter output directory path (default: /srv/homeassistant/media/day_photos): ").strip()
    if not output_dir:
        output_dir = "/srv/homeassistant/media/day_photos"
    
    print("\n" + "="*50)
    
    # Get date format
    print("Select date format in your photo filenames:")
    print("1. YYYY-MM-DD (e.g., 2024-01-15_photo.jpg)")
    print("2. YYYY_MM_DD (e.g., 2024_01_15_photo.jpg)")
    print("3. YYYYMMDD (e.g., 20240115_photo.jpg)")
    print("4. MM-DD-YYYY (e.g., 01-15-2024_photo.jpg)")
    print("5. Other (will use EXIF data and file modification time)")
    
    format_choice = input("Enter choice (1-5, default: 5): ").strip()
    
    date_formats = {
        "1": "YYYY-MM-DD",
        "2": "YYYY_MM_DD", 
        "3": "YYYYMMDD",
        "4": "MM-DD-YYYY",
        "5": "EXIF"
    }
    
    date_format = date_formats.get(format_choice, "EXIF")
    
    print("\n" + "="*50)
    
    # Test photo finding
    years_back = input("How many years back to test? (default: 2): ").strip()
    years_back = int(years_back) if years_back.isdigit() else 2
    
    if not test_photo_finding(source_dir, years_back):
        print("\n❌ Setup failed - photo finding test failed!")
        sys.exit(1)
    
    print("\n" + "="*50)
    
    # Setup Airflow variables
    setup_airflow = input("Set up Airflow variables? (y/n): ").strip().lower()
    if setup_airflow == 'y':
        setup_airflow_variables(source_dir, output_dir, date_format)
    
    print("\n" + "="*50)
    
    # Final instructions
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy local_photos_dag.py to your Airflow dags/ folder")
    print("2. Copy local_photos_fetcher.py to your Airflow dags/ folder")
    print("3. Update the SOURCE_DIR in local_photos_dag.py to match your path")
    print("4. Ensure the output directory exists and is writable")
    print("5. Restart Airflow webserver and scheduler")
    print("6. The DAG will run daily at 4:00 AM")
    print("\nAdvantages over cloud solutions:")
    print("- No 2FA issues or device trust problems")
    print("- No cloud sync required")
    print("- Works with any organized photo directory")
    print("- Faster execution (no network downloads)")
    print("- No API rate limits or restrictions")


if __name__ == "__main__":
    main() 