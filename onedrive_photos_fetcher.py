"""
Simplified OneDrive Photos Fetcher for Airflow

This module provides a reliable way to fetch photos from OneDrive using
direct OAuth authentication, bypassing the problematic O365 library.
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
from requests_oauthlib import OAuth2Session

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleOneDrivePhotosFetcher:
    """Simplified OneDrive photos fetcher with reliable OAuth authentication."""
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_file: str = "onedrive_token.pickle",
        output_dir: str = "./images",
        photos_folder: str = "Pictures"  # OneDrive photos folder name
    ):
        self.client_id = client_id or os.getenv("ONEDRIVE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("ONEDRIVE_CLIENT_SECRET")
        self.token_file = Path(token_file)
        self.output_dir = Path(output_dir)
        self.photos_folder = photos_folder
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Client ID and Client Secret must be provided either as parameters or via ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET environment variables")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _save_token(self, token_data: Dict[str, Any]) -> None:
        """Save token to file."""
        try:
            with open(self.token_file, 'wb') as f:
                pickle.dump(token_data, f)
            logger.info("Saved OneDrive authentication token")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")
    
    def _load_token(self) -> Optional[Dict[str, Any]]:
        """Load token from file."""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as f:
                    token_data = pickle.load(f)
                
                # Check if token is still valid
                if 'expires_at' in token_data:
                    if datetime.now().timestamp() < token_data['expires_at']:
                        logger.info("Loaded existing valid OneDrive token")
                        return token_data
                    else:
                        logger.info("Existing token expired")
                else:
                    logger.info("Loaded existing OneDrive token")
                    return token_data
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
        return None
    
    def authenticate(self) -> bool:
        """Authenticate with OneDrive using reliable OAuth."""
        # Try to load existing token first
        if self._load_token():
            return True
        
        # Use simple OAuth approach for more reliable authentication
        try:
            # Create OAuth session
            oauth = OAuth2Session(
                self.client_id,
                redirect_uri="https://login.microsoftonline.com/common/oauth2/nativeclient",
                scope=["Files.Read.All"]
            )
            
            # Get authentication URL
            auth_url, state = oauth.authorization_url(
                "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
            )
            
            print("\n1. Go to this URL in your browser:")
            print("=" * 80)
            print(auth_url)
            print("=" * 80)
            print("2. Sign in with your Microsoft account")
            print("3. Grant permissions to the app")
            print("4. Copy the authorization code from the redirect URL")
            print("\n⚠️ IMPORTANT: Use the code immediately after getting it!")
            
            auth_code = input("\nEnter the authorization code: ").strip()
            
            if not auth_code:
                logger.error("No authorization code provided")
                return False
            
            # Exchange authorization code for access token
            try:
                token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
                token_data = {
                    'grant_type': 'authorization_code',
                    'code': auth_code,
                    'redirect_uri': "https://login.microsoftonline.com/common/oauth2/nativeclient",
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }
                
                response = oauth.post(token_url, data=token_data)
                
                if response.status_code == 200:
                    token_info = response.json()
                    logger.info("Successfully authenticated with OneDrive")
                    
                    # Calculate expiration time
                    if 'expires_in' in token_info:
                        token_info['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
                    
                    # Save token for future use
                    self._save_token(token_info)
                    
                    return True
                else:
                    logger.error(f"Token exchange failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return False
                    
            except Exception as e:
                logger.error(f"Token exchange failed: {e}")
                logger.error("This might be due to an expired authorization code")
                logger.error("Try getting a fresh authorization code from the URL")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def search_photos_for_date(
        self, 
        target_date: datetime, 
        years_back: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for photos on a specific date across multiple years."""
        token_data = self._load_token()
        if not token_data:
            logger.error("No valid token found")
            return []
        
        photos_found = []
        
        for year_offset in range(1, years_back + 1):
            past_date = target_date.replace(year=target_date.year - year_offset)
            start_date = past_date
            end_date = past_date + timedelta(days=1)
            
            logger.info(f"Searching for photos on {past_date.date()}")
            
            try:
                # Use Microsoft Graph API to search for files
                headers = {
                    'Authorization': f"Bearer {token_data['access_token']}",
                    'Content-Type': 'application/json'
                }
                
                # Search for files in OneDrive
                search_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
                params = {
                    '$filter': f"file ne null and createdDateTime ge {start_date.isoformat()}Z and createdDateTime lt {end_date.isoformat()}Z"
                }
                
                response = requests.get(search_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    files_data = response.json()
                    files = files_data.get('value', [])
                    
                    # Filter for image files
                    image_files = [f for f in files if f.get('file', {}).get('mimeType', '').startswith('image/')]
                    
                    logger.info(f"Found {len(image_files)} photos for {past_date.date()}")
                    
                    for file in image_files:
                        photos_found.append({
                            'file': file,
                            'date': past_date.date(),
                            'year_offset': year_offset
                        })
                else:
                    logger.error(f"Failed to search files: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error searching photos for {past_date.date()}: {e}")
        
        return photos_found
    
    def download_photos(
        self, 
        photos_data: List[Dict[str, Any]], 
        skip_existing: bool = True
    ) -> List[Path]:
        """Download photos to local directory."""
        token_data = self._load_token()
        if not token_data:
            logger.error("No valid token found")
            return []
        
        downloaded_files = []
        
        for photo_data in photos_data:
            file_info = photo_data['file']
            date = photo_data['date']
            
            try:
                # Create filename with date prefix for organization
                filename = file_info.get('name', 'unknown')
                file_extension = filename.split('.')[-1].lower()
                new_filename = f"{date}_{file_info['id']}.{file_extension}"
                file_path = self.output_dir / new_filename
                
                # Skip if file already exists
                if skip_existing and file_path.exists():
                    logger.info(f"Skipping existing file: {new_filename}")
                    downloaded_files.append(file_path)
                    continue
                
                # Download the file
                logger.info(f"Downloading: {new_filename}")
                
                download_url = file_info.get('@microsoft.graph.downloadUrl')
                if download_url:
                    response = requests.get(download_url)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        
                        downloaded_files.append(file_path)
                        logger.info(f"Successfully downloaded: {new_filename}")
                    else:
                        logger.error(f"Failed to download {filename}: HTTP {response.status_code}")
                else:
                    logger.error(f"No download URL for {filename}")
                
            except Exception as e:
                logger.error(f"Failed to download {filename}: {e}")
        
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
        raise ValueError("Client ID and Client Secret must be provided")
    
    # Parse target date
    if target_date:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        parsed_date = datetime.now()
    
    # Create fetcher and download photos
    fetcher = SimpleOneDrivePhotosFetcher(
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