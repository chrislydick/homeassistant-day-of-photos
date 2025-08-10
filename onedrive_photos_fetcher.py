"""
OneDrive Photos Fetcher for Airflow

This module provides a robust way to fetch photos from OneDrive with
improved OAuth handling and session management. OneDrive has a more
reliable API than iCloud and better integration with Microsoft accounts.
"""

from __future__ import annotations

import logging
import os
import pickle
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from dotenv import load_dotenv
import webbrowser
import time
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneDrivePhotosFetcher:
    """Enhanced OneDrive photos fetcher with improved OAuth handling."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_file: str = "onedrive_token.pickle",
        output_dir: str = "./images",
        photos_folder: str = "Pictures"  # OneDrive photos folder name
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
            print("1. Opening browser for authentication...")
            print("2. Sign in with your Microsoft account")
            print("3. Grant permissions to the app")
            print("4. Copy the authorization code from the URL")
            print()
            
            # Open browser
            try:
                webbrowser.open(auth_url)
            except:
                print(f"Please open this URL in your browser:\n{auth_url}")
            
            print("Waiting for authorization code...")
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
            
            # Search for photos in the Pictures folder
            search_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{self.photos_folder}:/children"
            
            response = requests.get(search_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                items = response.json().get('value', [])
                
                for item in items:
                    if item.get('file'):  # Check if it's a file
                        file_extension = Path(item['name']).suffix.lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef']:
                            photo_date = self._get_photo_date(item)
                            
                            if photo_date:
                                # Check if photo is from the same day across multiple years
                                for year_offset in range(1, years_back + 1):
                                    past_year = target_date.year - year_offset
                                    search_date = datetime(past_year, month_day[0], month_day[1])
                                    
                                    if photo_date.date() == search_date.date():
                                        photos_found.append({
                                            'item': item,
                                            'date': search_date.date(),
                                            'year_offset': year_offset,
                                            'photo_date': photo_date
                                        })
                
                logger.info(f"Found {len(photos_found)} photos for {target_date.date()} going back {years_back} years")
                    
        except Exception as e:
            logger.error(f"Error searching photos: {e}")
        
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


def fetch_onedrive_photos_airflow(
    target_date: Optional[str] = None,
    years_back: int = 5,
    output_dir: str = "./images",
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    token_file: str = "onedrive_token.pickle",
    photos_folder: str = "Pictures"
) -> None:
    """
    Airflow-compatible function to fetch photos from OneDrive.
    
    Args:
        target_date: Date string in YYYY-MM-DD format (defaults to today)
        years_back: Number of years to look back
        output_dir: Directory to save downloaded photos
        client_id: OneDrive app client ID (from Airflow variables)
        client_secret: OneDrive app client secret (from Airflow variables)
        token_file: Path to token file for persistent authentication
        photos_folder: OneDrive folder containing photos
    """
    if not client_id or not client_secret:
        raise ValueError("Client ID and client secret must be provided")
    
    # Parse target date
    if target_date:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        parsed_date = datetime.now()
    
    # Create fetcher and download photos
    fetcher = OneDrivePhotosFetcher(
        client_id=client_id,
        client_secret=client_secret,
        token_file=token_file,
        output_dir=output_dir,
        photos_folder=photos_folder
    )
    
    downloaded_files = fetcher.fetch_and_download(
        target_date=parsed_date,
        years_back=years_back,
        skip_existing=True
    )
    
    logger.info(f"Airflow task completed. Downloaded {len(downloaded_files)} photos")


if __name__ == "__main__":
    # For testing outside of Airflow
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch OneDrive photos for a date")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--years-back", type=int, default=5)
    parser.add_argument("--output-dir", default="./images")
    parser.add_argument("--client-id", required=True, help="OneDrive app client ID")
    parser.add_argument("--client-secret", required=True, help="OneDrive app client secret")
    parser.add_argument("--token-file", default="onedrive_token.pickle", help="Path to token file")
    parser.add_argument("--photos-folder", default="Pictures", help="OneDrive photos folder name")
    
    args = parser.parse_args()
    
    fetch_onedrive_photos_airflow(
        target_date=args.date,
        years_back=args.years_back,
        output_dir=args.output_dir,
        client_id=args.client_id,
        client_secret=args.client_secret,
        token_file=args.token_file,
        photos_folder=args.photos_folder
    ) 