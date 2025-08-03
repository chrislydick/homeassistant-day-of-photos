"""
Dropbox Photos Fetcher for Airflow

This module provides a robust way to fetch photos from Dropbox with
improved OAuth handling and session management. Dropbox has a more
reliable API than iCloud and doesn't have the same 2FA device trust issues.
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

try:
    import dropbox
    from dropbox import DropboxOAuth2FlowNoRedirect
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DropboxPhotosFetcher:
    """Enhanced Dropbox photos fetcher with improved OAuth handling."""
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        token_file: str = "dropbox_token.pickle",
        output_dir: str = "./images",
        photos_folder: str = "/Photos"  # Dropbox photos folder path
    ):
        self.app_key = app_key
        self.app_secret = app_secret
        self.token_file = Path(token_file)
        self.output_dir = Path(output_dir)
        self.photos_folder = photos_folder
        self.dbx = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_token(self) -> bool:
        """Load existing token if available."""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as f:
                    token_data = pickle.load(f)
                
                if token_data and 'access_token' in token_data:
                    self.dbx = dropbox.Dropbox(token_data['access_token'])
                    # Test the token
                    self.dbx.users_get_current_account()
                    logger.info("Loaded existing valid Dropbox token")
                    return True
                else:
                    logger.warning("Token file is invalid")
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
            logger.info("Saved Dropbox authentication token")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")
    
    def authenticate(self) -> bool:
        """Authenticate with Dropbox API."""
        if not DROPBOX_AVAILABLE:
            logger.error("Dropbox library is not installed. Install with: pip install dropbox")
            return False
        
        # Try to load existing token first
        if self._load_token():
            return True
        
        # Create new authentication flow
        try:
            auth_flow = DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
            
            # Get authorization URL
            authorize_url = auth_flow.start()
            print(f"\n1. Go to: {authorize_url}")
            print("2. Click 'Allow' (you might have to log in first)")
            print("3. Copy the authorization code")
            
            auth_code = input("\nEnter the authorization code: ").strip()
            
            if not auth_code:
                logger.error("No authorization code provided")
                return False
            
            # Exchange authorization code for access token
            oauth_result = auth_flow.finish(auth_code)
            
            # Create Dropbox client
            self.dbx = dropbox.Dropbox(oauth_result.access_token)
            
            # Test authentication
            account = self.dbx.users_get_current_account()
            logger.info(f"Successfully authenticated as: {account.name.display_name}")
            
            # Save token for future use
            self._save_token({
                'access_token': oauth_result.access_token,
                'refresh_token': getattr(oauth_result, 'refresh_token', None),
                'expires_at': getattr(oauth_result, 'expires_at', None)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _get_photo_date(self, file_path: str, metadata: dropbox.files.FileMetadata) -> Optional[datetime]:
        """Extract date from photo file using multiple methods."""
        try:
            # Method 1: Try to get date from filename patterns
            filename = Path(file_path).stem.lower()
            
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
            
            # Method 2: Use file modification time from Dropbox metadata
            if hasattr(metadata, 'server_modified'):
                return metadata.server_modified
            
            # Method 3: Use client modification time
            if hasattr(metadata, 'client_modified'):
                return metadata.client_modified
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not extract date from {file_path}: {e}")
            return None
    
    def search_photos_for_date(
        self, 
        target_date: datetime, 
        years_back: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for photos from the same day across multiple years."""
        if not self.dbx:
            logger.error("Not authenticated")
            return []
        
        photos_found = []
        month_day = (target_date.month, target_date.day)
        
        logger.info(f"Searching for photos on {target_date.date()} going back {years_back} years")
        
        for year_offset in range(1, years_back + 1):
            past_year = target_date.year - year_offset
            search_date = datetime(past_year, month_day[0], month_day[1])
            
            logger.info(f"Searching for photos on {search_date.date()}")
            
            try:
                # List files in the photos folder
                result = self.dbx.files_list_folder(
                    path=self.photos_folder,
                    recursive=True,
                    include_media_info=True
                )
                
                # Process all files
                for entry in result.entries:
                    if isinstance(entry, dropbox.files.FileMetadata):
                        # Check if it's a photo file
                        file_extension = Path(entry.name).suffix.lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef']:
                            photo_date = self._get_photo_date(entry.path_display, entry)
                            
                            if photo_date and photo_date.date() == search_date.date():
                                photos_found.append({
                                    'entry': entry,
                                    'date': search_date.date(),
                                    'year_offset': year_offset,
                                    'photo_date': photo_date
                                })
                
                # Handle pagination
                while result.has_more:
                    result = self.dbx.files_list_folder_continue(result.cursor)
                    for entry in result.entries:
                        if isinstance(entry, dropbox.files.FileMetadata):
                            file_extension = Path(entry.name).suffix.lower()
                            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef']:
                                photo_date = self._get_photo_date(entry.path_display, entry)
                                
                                if photo_date and photo_date.date() == search_date.date():
                                    photos_found.append({
                                        'entry': entry,
                                        'date': search_date.date(),
                                        'year_offset': year_offset,
                                        'photo_date': photo_date
                                    })
                
                logger.info(f"Found {len([p for p in photos_found if p['date'] == search_date.date()])} photos for {search_date.date()}")
                    
            except Exception as e:
                logger.error(f"Error searching photos for {search_date.date()}: {e}")
        
        return photos_found
    
    def download_photos(
        self, 
        photos_data: List[Dict[str, Any]], 
        skip_existing: bool = True
    ) -> List[Path]:
        """Download photos to local directory."""
        downloaded_files = []
        
        for photo_data in photos_data:
            entry = photo_data['entry']
            date = photo_data['date']
            
            try:
                # Create filename with date prefix for organization
                file_extension = Path(entry.name).suffix.lower()
                filename = f"{date}_{entry.name}"
                file_path = self.output_dir / filename
                
                # Skip if file already exists
                if skip_existing and file_path.exists():
                    logger.info(f"Skipping existing file: {filename}")
                    downloaded_files.append(file_path)
                    continue
                
                # Download the photo
                logger.info(f"Downloading: {filename}")
                
                # Download file from Dropbox
                metadata, response = self.dbx.files_download(entry.path_display)
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_files.append(file_path)
                logger.info(f"Successfully downloaded: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to download {entry.name}: {e}")
        
        return downloaded_files
    
    def fetch_and_download(
        self, 
        target_date: Optional[datetime] = None,
        years_back: int = 5,
        skip_existing: bool = True
    ) -> List[Path]:
        """Main method to fetch and download photos for a date."""
        if not self.authenticate():
            raise RuntimeError("Failed to authenticate with Dropbox")
        
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


def fetch_dropbox_photos_airflow(
    target_date: Optional[str] = None,
    years_back: int = 5,
    output_dir: str = "./images",
    app_key: Optional[str] = None,
    app_secret: Optional[str] = None,
    token_file: str = "dropbox_token.pickle",
    photos_folder: str = "/Photos"
) -> None:
    """
    Airflow-compatible function to fetch photos from Dropbox.
    
    Args:
        target_date: Date string in YYYY-MM-DD format (defaults to today)
        years_back: Number of years to look back
        output_dir: Directory to save downloaded photos
        app_key: Dropbox app key (from Airflow variables)
        app_secret: Dropbox app secret (from Airflow variables)
        token_file: Path to token file for persistent authentication
        photos_folder: Dropbox folder containing photos
    """
    if not app_key or not app_secret:
        raise ValueError("App key and app secret must be provided")
    
    # Parse target date
    if target_date:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        parsed_date = datetime.now()
    
    # Create fetcher and download photos
    fetcher = DropboxPhotosFetcher(
        app_key=app_key,
        app_secret=app_secret,
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
    
    parser = argparse.ArgumentParser(description="Fetch Dropbox photos for a date")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--years-back", type=int, default=5)
    parser.add_argument("--output-dir", default="./images")
    parser.add_argument("--app-key", required=True, help="Dropbox app key")
    parser.add_argument("--app-secret", required=True, help="Dropbox app secret")
    parser.add_argument("--token-file", default="dropbox_token.pickle", help="Path to token file")
    parser.add_argument("--photos-folder", default="/Photos", help="Dropbox photos folder path")
    
    args = parser.parse_args()
    
    fetch_dropbox_photos_airflow(
        target_date=args.date,
        years_back=args.years_back,
        output_dir=args.output_dir,
        app_key=args.app_key,
        app_secret=args.app_secret,
        token_file=args.token_file,
        photos_folder=args.photos_folder
    ) 