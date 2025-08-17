#!/usr/bin/env python3
"""
OneDrive Photos Script - Standalone version

This script fetches photos from OneDrive for a specific date across multiple years
and transfers them to a Home Assistant server. Designed to be run via crontab.

Usage:
    python3 onedrive_photos_script.py
    # or with custom date:
    python3 onedrive_photos_script.py --date 2024-12-25
"""

import argparse
import logging
import os
import pickle
import requests
import subprocess
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from dotenv import load_dotenv
import webbrowser
import time
from urllib.parse import urlparse, parse_qs
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('onedrive_photos.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OneDrivePhotosFetcher:
    """Enhanced OneDrive photos fetcher with improved OAuth handling."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_file: str = "./onedrive_token.pickle",
        output_dir: str = "./images",
        photos_folder: str = "My files/Pictures/Camera Roll"  # OneDrive photos folder name
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = Path(token_file)
        self.output_dir = Path(output_dir)
        self.photos_folder = photos_folder
        self.access_token = None
        self.refresh_token = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_token(self) -> bool:
        """Load existing token if available."""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as f:
                    token_data = pickle.load(f)
                
                if token_data and 'access_token' in token_data:
                    self.access_token = token_data['access_token']
                    self.refresh_token = token_data.get('refresh_token')
                    
                    # Test the token
                    if self._test_token():
                        logger.info("Loaded existing valid OneDrive token")
                        return True
                    else:
                        logger.warning("Token is invalid or expired, trying refresh")
                        return self._refresh_token()
                else:
                    logger.warning("Token file is empty or invalid")
                    return False
                    
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
                return False
        return False
    
    def _save_token(self, token_data: dict) -> None:
        """Save token for future use."""
        try:
            with open(self.token_file, 'wb') as f:
                pickle.dump(token_data, f)
            logger.info("Saved OneDrive authentication token")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")
    
    def _test_token(self) -> bool:
        """Test if the current access token is valid."""
        if not self.access_token:
            return False
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me/drive',
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Token test failed: {e}")
            return False
    
    def _refresh_token(self) -> bool:
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            return False
            
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data.get('refresh_token', self.refresh_token)
                
                # Save updated token
                self._save_token({
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token
                })
                
                logger.info("Successfully refreshed OneDrive token")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Authenticate with OneDrive API using direct OAuth2."""
        # Try to load existing token first
        if self._load_token():
            return True
        
        # Start OAuth2 flow
        try:
            # Step 1: Get authorization URL
            auth_url = (
                "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
                f"client_id={self.client_id}&"
                "response_type=code&"
                "redirect_uri=http://localhost:8080&"
                "scope=Files.Read.All&"
                "response_mode=query"
            )
            
            print("\n🔐 OneDrive Authentication")
            print("=" * 50)
            print("1. Go to this URL in your browser:")
            print("=" * 80)
            print(auth_url)
            print("=" * 80)
            print("2. Sign in with your Microsoft account")
            print("3. Grant permissions to the app")
            print("4. Copy the authorization code from the redirect URL")
            print()
            
            # Try to open browser as well
            try:
                webbrowser.open(auth_url)
                print("✅ Browser opened automatically")
            except:
                print("⚠️  Could not open browser automatically")
            
            print("\nWaiting for authorization code...")
            auth_code = input("Enter the authorization code from the URL: ").strip()
            
            if not auth_code:
                logger.error("No authorization code provided")
                return False
            
            # Step 2: Exchange authorization code for tokens
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'http://localhost:8080'
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.refresh_token = token_data.get('refresh_token')
                
                # Save token for future use
                self._save_token({
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token
                })
                
                logger.info("Successfully authenticated with OneDrive")
                return True
            else:
                logger.error(f"Token exchange failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _get_photo_date(self, file_item) -> Optional[datetime]:
        """Extract date from photo file using multiple methods."""
        try:
            # Method 1: Try to get date from filename patterns
            filename = Path(file_item['name']).stem.lower()
            
            # Common filename patterns
            patterns = [
                r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
                r"(\d{4})_(\d{2})_(\d{2})",  # YYYY_MM_DD
                r"(\d{4})(\d{2})(\d{2})",    # YYYYMMDD
                r"(\d{2})-(\d{2})-(\d{4})",  # MM-DD-YYYY
                r"(\d{2})_(\d{2})_(\d{4})",  # MM_DD_YYYY
                r"^(\d{4})(\d{2})(\d{2})_",  # YYYYMMDD_ (at start of filename)
            ]
            
            import re
            for pattern in patterns:
                match = re.search(pattern, filename)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        if len(groups[0]) == 4:  # YYYY-MM-DD or YYYY_MM_DD or YYYYMMDD
                            year, month, day = groups
                        else:  # MM-DD-YYYY or MM_DD_YYYY
                            month, day, year = groups
                        return datetime(int(year), int(month), int(day))
            
            # Method 2: Use file creation time from OneDrive metadata
            if 'createdDateTime' in file_item:
                return datetime.fromisoformat(file_item['createdDateTime'].replace('Z', '+00:00'))
            
            # Method 3: Use file modification time
            if 'lastModifiedDateTime' in file_item:
                return datetime.fromisoformat(file_item['lastModifiedDateTime'].replace('Z', '+00:00'))
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not extract date from {file_item['name']}: {e}")
            return None
    
    def search_photos_for_date(
        self, 
        target_date: datetime, 
        years_back: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for photos from the same day across multiple years."""
        if not self.access_token:
            logger.error("Not authenticated")
            return []
        
        photos_found = []
        month_day = (target_date.month, target_date.day)
        
        logger.info(f"Searching for photos on {target_date.date()} going back {years_back} years")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Optimized search: only look in relevant month folders for each year
            photos_found = self._search_optimized_by_month(
                target_date=target_date,
                years_back=years_back,
                headers=headers,
                day_range=day_range
            )
                
            logger.info(f"Found {len(photos_found)} photos for {target_date.date()} going back {years_back} years")
                    
        except Exception as e:
            logger.error(f"Error searching photos: {e}")
        
        return photos_found
    
    def _search_optimized_by_month(
        self,
        target_date: datetime,
        years_back: int,
        headers: dict,
        day_range: int = 0
    ) -> List[Dict[str, Any]]:
        """Optimized search that only looks in relevant month folders."""
        photos_found = []
        
        # Generate list of dates to search (target date ± day_range)
        dates_to_search = []
        for day_offset in range(-day_range, day_range + 1):
            search_date = target_date + timedelta(days=day_offset)
            dates_to_search.append(search_date)
        
        logger.info(f"🔍 Optimized search: looking for {len(dates_to_search)} dates (±{day_range} days)")
        
        # Search for each date across all years
        for search_date in dates_to_search:
            month_day = (search_date.month, search_date.day)
            month_str = f"{month_day[0]:02d}"
            
            logger.info(f"🔍 Searching for date {search_date.date()} (month {month_str})")
            
            # Search for each year back
            for year_offset in range(1, years_back + 1):
                past_year = target_date.year - year_offset
                historical_date = datetime(past_year, month_day[0], month_day[1])
                
                logger.info(f"  🔍 Year {past_year}, month {month_str}")
                
                # Try to access the specific year/month folder directly
                year_month_path = f"{self.photos_folder}/{past_year}/{month_str}"
                photos_in_year = self._search_specific_month_folder(
                    year_month_path=year_month_path,
                    search_date=historical_date,
                    headers=headers
                )
                
                photos_found.extend(photos_in_year)
        
        return photos_found
    
    def _search_specific_month_folder(
        self,
        year_month_path: str,
        search_date: datetime,
        headers: dict
    ) -> List[Dict[str, Any]]:
        """Search a specific year/month folder for photos."""
        photos_found = []
        
        try:
            # Try to access the specific year/month folder
            search_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{year_month_path}:/children"
            response = requests.get(search_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                items = response.json().get('value', [])
                logger.info(f"  📁 Found {len(items)} items in {year_month_path}")
                
                for item in items:
                    if item.get('file'):
                        # Check if it's a photo file
                        file_extension = Path(item['name']).suffix.lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef']:
                            photo_date = self._get_photo_date(item)
                            
                            if photo_date and photo_date.date() == search_date.date():
                                logger.info(f"  📸 Found matching photo: {item['name']} ({photo_date.date()})")
                                photos_found.append({
                                    'item': item,
                                    'date': search_date.date(),
                                    'year_offset': search_date.year,
                                    'photo_date': photo_date,
                                    'folder_path': year_month_path
                                })
            else:
                logger.info(f"  ⚠️ Month folder not found: {year_month_path} (status: {response.status_code})")
                
        except Exception as e:
            logger.error(f"  ❌ Error searching {year_month_path}: {e}")
        
        return photos_found
    
    def _search_folder_recursively(
        self,
        folder_id: Optional[str],
        folder_path: str,
        target_date: datetime,
        years_back: int,
        headers: dict,
        depth: int = 0,
        max_depth: int = 10  # Prevent infinite recursion
    ) -> List[Dict[str, Any]]:
        """Recursively search through folders for photos."""
        photos_found = []
        month_day = (target_date.month, target_date.day)
        
        if depth > max_depth:
            logger.warning(f"Reached maximum search depth ({max_depth}) for {folder_path}")
            return photos_found
        
        try:
            # Construct the URL based on whether we have a folder ID or path
            if folder_id:
                search_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            else:
                search_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}:/children"
            
            response = requests.get(search_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                items = response.json().get('value', [])
                logger.info(f"{'  ' * depth}📁 Searching {folder_path}: {len(items)} items")
                
                for item in items:
                    if item.get('folder'):
                        # Recursively search subfolders
                        subfolder_path = f"{folder_path}/{item['name']}"
                        sub_photos = self._search_folder_recursively(
                            folder_id=item['id'],
                            folder_path=subfolder_path,
                            target_date=target_date,
                            years_back=years_back,
                            headers=headers,
                            depth=depth + 1,
                            max_depth=max_depth
                        )
                        photos_found.extend(sub_photos)
                        
                    elif item.get('file'):
                        # Check if it's a photo file
                        file_extension = Path(item['name']).suffix.lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef']:
                            photo_date = self._get_photo_date(item)
                            
                            if photo_date:
                                # Check if photo is from the same day across multiple years
                                for year_offset in range(1, years_back + 1):
                                    past_year = target_date.year - year_offset
                                    search_date = datetime(past_year, month_day[0], month_day[1])
                                    
                                    if photo_date.date() == search_date.date():
                                        logger.info(f"{'  ' * depth}📸 Found matching photo: {item['name']} ({photo_date.date()})")
                                        photos_found.append({
                                            'item': item,
                                            'date': search_date.date(),
                                            'year_offset': year_offset,
                                            'photo_date': photo_date,
                                            'folder_path': folder_path
                                        })
            else:
                logger.error(f"Failed to access folder {folder_path}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error searching folder {folder_path}: {e}")
        
        return photos_found
    
    def download_photos(
        self, 
        photos_data: List[Dict[str, Any]], 
        skip_existing: bool = True
    ) -> List[Path]:
        """Download photos to local directory."""
        downloaded_files = []
        
        for photo_data in photos_data:
            item = photo_data['item']
            date = photo_data['date']
            
            try:
                # Create filename with date prefix for organization
                file_extension = Path(item['name']).suffix.lower()
                filename = f"{date}_{item['name']}"
                file_path = self.output_dir / filename
                
                # Skip if file already exists
                if skip_existing and file_path.exists():
                    logger.info(f"Skipping existing file: {filename}")
                    downloaded_files.append(file_path)
                    continue
                
                # Download the photo
                logger.info(f"Downloading: {filename}")
                
                # Download file from OneDrive using the download URL
                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                }
                
                download_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item['id']}/content"
                
                with open(file_path, 'wb') as f:
                    response = requests.get(download_url, headers=headers, stream=True, timeout=30)
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    else:
                        logger.error(f"Failed to download {item['name']}: {response.status_code}")
                        continue
                
                # Convert HEIC to JPG if needed
                if file_extension == '.heic':
                    logger.info(f"Converting HEIC to JPG: {filename}")
                    jpg_path = convert_heic_to_jpg(file_path)
                    if jpg_path:
                        # Remove the original HEIC file
                        file_path.unlink()
                        downloaded_files.append(jpg_path)
                        logger.info(f"✅ Successfully converted and saved: {jpg_path.name}")
                    else:
                        logger.warning(f"⚠️ HEIC conversion failed or not supported, keeping original: {filename}")
                        downloaded_files.append(file_path)
                else:
                    downloaded_files.append(file_path)
                    logger.info(f"Successfully downloaded: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to download {item['name']}: {e}")
        
        return downloaded_files
    
    def fetch_and_download(
        self, 
        target_date: Optional[datetime] = None,
        years_back: int = 5,
        skip_existing: bool = True
    ) -> List[Path]:
        """Main method to fetch and download photos for a date."""
        if not self.authenticate():
            raise RuntimeError("Failed to authenticate with OneDrive")
        
        if target_date is None:
            target_date = datetime.now()
        
        logger.info(f"Fetching photos for {target_date.date()} going back {years_back} years")
        
        # Search for photos
        photos_data = self.search_photos_for_date(target_date, years_back)
        
        if not photos_data:
            logger.info("No photos found")
            return []
        
        # Download photos
        downloaded_files = self.download_photos(photos_data, skip_existing)
        
        logger.info(f"Downloaded {len(downloaded_files)} photos to {self.output_dir}")
        return downloaded_files


def convert_heic_to_jpg(heic_path: Path) -> Optional[Path]:
    """Convert HEIC file to JPG format."""
    try:
        # Check if HEIC support is available
        try:
            # Try to import HEIF support
            import pillow_heif
            pillow_heif.register_heif_opener()
            logger.info("✅ HEIC support available via pillow-heif")
        except ImportError:
            logger.warning("⚠️ HEIC support not available. Install with: pip install pillow-heif")
            logger.warning("⚠️ Skipping HEIC conversion, keeping original file")
            return None
        
        # Open HEIC image
        with Image.open(heic_path) as img:
            # Convert to RGB (JPG doesn't support alpha channel)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create JPG filename
            jpg_path = heic_path.with_suffix('.jpg')
            
            # Save as JPG with high quality
            img.save(jpg_path, 'JPEG', quality=95, optimize=True)
            
            logger.info(f"✅ Converted {heic_path.name} to {jpg_path.name}")
            return jpg_path
            
    except Exception as e:
        logger.error(f"❌ Failed to convert {heic_path.name}: {e}")
        logger.error(f"   Error details: {type(e).__name__}: {str(e)}")
        return None


def cleanup_remote_folder(remote_host, remote_user, remote_dir, ssh_port="22"):
    """Remove all files in the remote media folder before transferring new ones."""
    try:
        # Remove all files in the remote directory
        cleanup_cmd = f"ssh -p {ssh_port} {remote_user}@{remote_host} 'rm -rf {remote_dir}/*'"
        result = subprocess.run(cleanup_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ Cleaned up remote folder {remote_dir}")
            return True
        else:
            logger.warning(f"⚠️ Cleanup command returned non-zero: {result.stderr}")
            # Don't fail the entire process if cleanup fails
            return True
            
    except Exception as e:
        logger.warning(f"⚠️ Error during cleanup: {e}")
        # Don't fail the entire process if cleanup fails
        return True


def transfer_photos_to_homeassistant(local_dir, remote_host, remote_user, remote_dir, ssh_port="22", cleanup=True):
    """Transfer photos from local server to Home Assistant server via SCP"""
    try:
        # Clean up the remote folder if requested
        if cleanup:
            cleanup_remote_folder(remote_host, remote_user, remote_dir, ssh_port)
        
        # Create remote directory if it doesn't exist
        ssh_cmd = f"ssh -p {ssh_port} {remote_user}@{remote_host} 'mkdir -p {remote_dir}'"
        subprocess.run(ssh_cmd, shell=True, check=True)
        
        # Transfer files
        scp_cmd = f"scp -P {ssh_port} -r {local_dir}/* {remote_user}@{remote_host}:{remote_dir}/"
        result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully transferred photos to {remote_host}:{remote_dir}")
            return True
        else:
            logger.error(f"❌ Failed to transfer photos: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error transferring photos: {e}")
        return False


def main():
    """Main function to run the OneDrive photos script."""
    parser = argparse.ArgumentParser(description="Fetch OneDrive photos for a date and transfer to Home Assistant")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--years-back", type=int, default=10, help="Number of years to look back")
    parser.add_argument("--day-range", type=int, default=1, help="Number of days before/after target date to include (e.g., 1 = ±1 day)")
    parser.add_argument("--output-dir", default="/tmp/onedrive_photos_temp", help="Local temporary directory")
    parser.add_argument("--client-id", help="OneDrive app client ID (from env var ONEDRIVE_CLIENT_ID)")
    parser.add_argument("--client-secret", help="OneDrive app client secret (from env var ONEDRIVE_CLIENT_SECRET)")
    parser.add_argument("--token-file", default="./onedrive_token.pickle", help="Path to token file")
    parser.add_argument("--photos-folder", default="Pictures", help="OneDrive photos folder name")
    parser.add_argument("--homeassistant-host", help="Home Assistant server host (from env var HOMEASSISTANT_HOST)")
    parser.add_argument("--homeassistant-user", help="Home Assistant server user (from env var HOMEASSISTANT_USER)")
    parser.add_argument("--homeassistant-photos-dir", help="Home Assistant photos directory (from env var HOMEASSISTANT_PHOTOS_DIR)")
    parser.add_argument("--homeassistant-ssh-port", help="Home Assistant SSH port (from env var HOMEASSISTANT_SSH_PORT)")
    parser.add_argument("--skip-transfer", action="store_true", help="Skip transferring to Home Assistant")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't clean up remote folder before transfer")
    
    args = parser.parse_args()
    
    # Get credentials from environment variables if not provided as arguments
    client_id = args.client_id or os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = args.client_secret or os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.error("ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET must be set in environment variables or provided as arguments")
        sys.exit(1)
    
    # Get Home Assistant configuration from environment variables if not provided as arguments
    homeassistant_host = args.homeassistant_host or os.getenv("HOMEASSISTANT_HOST")
    homeassistant_user = args.homeassistant_user or os.getenv("HOMEASSISTANT_USER")
    homeassistant_photos_dir = args.homeassistant_photos_dir or os.getenv("HOMEASSISTANT_PHOTOS_DIR")
    homeassistant_ssh_port = args.homeassistant_ssh_port or os.getenv("HOMEASSISTANT_SSH_PORT", "22")
    
    # Get years_back from environment variable if not provided as argument
    years_back = args.years_back
    if years_back == 10:  # If using default, check for env var
        env_years_back = os.getenv("ONEDRIVE_YEARS_BACK")
        if env_years_back:
            try:
                years_back = int(env_years_back)
            except ValueError:
                logger.warning(f"Invalid ONEDRIVE_YEARS_BACK value: {env_years_back}, using default")
    
    # Get day_range from environment variable if not provided as argument
    day_range = args.day_range
    if day_range == 1:  # If using default, check for env var
        env_day_range = os.getenv("ONEDRIVE_DAY_RANGE")
        if env_day_range:
            try:
                day_range = int(env_day_range)
            except ValueError:
                logger.warning(f"Invalid ONEDRIVE_DAY_RANGE value: {env_day_range}, using default")
    
    if not args.skip_transfer and (not homeassistant_host or not homeassistant_user or not homeassistant_photos_dir):
        logger.error("HOMEASSISTANT_HOST, HOMEASSISTANT_USER, and HOMEASSISTANT_PHOTOS_DIR must be set in environment variables or provided as arguments")
        sys.exit(1)
    
    # Parse target date
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = datetime.now()
    
    logger.info(f"Starting OneDrive photos script for {target_date.date()}")
    
    try:
        # Create fetcher and download photos
        fetcher = OneDrivePhotosFetcher(
            client_id=client_id,
            client_secret=client_secret,
            token_file=args.token_file,
            output_dir=args.output_dir,
            photos_folder=args.photos_folder
        )
        
        downloaded_files = fetcher.fetch_and_download(
            target_date=target_date,
            years_back=years_back,
            skip_existing=True
        )
        
        # Transfer photos to Home Assistant server if requested
        if not args.skip_transfer and downloaded_files:
            transfer_success = transfer_photos_to_homeassistant(
                args.output_dir,
                homeassistant_host,
                homeassistant_user,
                homeassistant_photos_dir,
                homeassistant_ssh_port,
                cleanup=not args.no_cleanup
            )
            
            if transfer_success:
                # Clean up local temporary files
                shutil.rmtree(args.output_dir, ignore_errors=True)
                logger.info("✅ Cleaned up local temporary files")
            else:
                logger.warning("⚠️  Transfer failed, keeping local files for debugging")
        elif args.skip_transfer:
            logger.info("Skipping transfer to Home Assistant as requested")
        else:
            logger.info("ℹ️  No photos downloaded, skipping transfer")
        
        logger.info(f"Script completed successfully. Downloaded {len(downloaded_files)} photos")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
