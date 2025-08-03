"""
Enhanced Google Photos Fetcher for Airflow

This module provides a robust way to fetch photos from Google Photos with
improved OAuth handling and session management. It's designed to work seamlessly
with Apache Airflow for daily execution.
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
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Photos API configuration
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
DISCOVERY_URL = 'https://photoslibrary.googleapis.com/$discovery/rest?version=v1'


class GooglePhotosFetcher:
    """Enhanced Google Photos fetcher with improved OAuth handling."""
    
    def __init__(
        self,
        credentials_file: str = "creds.json",
        token_file: str = "token.pickle",
        output_dir: str = "./images"
    ):
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.output_dir = Path(output_dir)
        self.service = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_token(self) -> bool:
        """Load existing token if available."""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                
                if creds and creds.valid:
                    logger.info("Loaded existing valid token")
                    return True
                elif creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired token")
                    creds.refresh(Request())
                    self._save_token(creds)
                    return True
                else:
                    logger.warning("Token is invalid and cannot be refreshed")
                    return False
                    
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
                return False
        return False
    
    def _save_token(self, creds) -> None:
        """Save token for future use."""
        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("Saved authentication token")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")
    
    def authenticate(self) -> bool:
        """Authenticate with Google Photos API."""
        if not GOOGLE_AVAILABLE:
            logger.error("Google API libraries are not installed")
            return False
        
        if not self.credentials_file.exists():
            logger.error(f"Credentials file not found: {self.credentials_file}")
            return False
        
        # Try to load existing token first
        if self._load_token():
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                self.service = build('photoslibrary', 'v1', credentials=creds, discoveryServiceUrl=DISCOVERY_URL)
                logger.info("Successfully authenticated with existing token")
                return True
            except Exception as e:
                logger.warning(f"Failed to use existing token: {e}")
        
        # Create new authentication flow
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
            self.service = build('photoslibrary', 'v1', credentials=creds, discoveryServiceUrl=DISCOVERY_URL)
            
            # Save token for future use
            self._save_token(creds)
            
            logger.info("Successfully authenticated with Google Photos")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def search_photos_for_date(
        self, 
        target_date: datetime, 
        years_back: int = 5,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for photos on a specific date across multiple years."""
        if not self.service:
            logger.error("Not authenticated")
            return []
        
        photos_found = []
        month_day = (target_date.month, target_date.day)
        
        for year_offset in range(1, years_back + 1):
            past_year = target_date.year - year_offset
            start_date = datetime(past_year, month_day[0], month_day[1])
            end_date = start_date + timedelta(days=1)
            
            logger.info(f"Searching for photos on {start_date.date()}")
            
            try:
                date_range = {
                    'startDate': {
                        'year': start_date.year,
                        'month': start_date.month,
                        'day': start_date.day
                    },
                    'endDate': {
                        'year': end_date.year,
                        'month': end_date.month,
                        'day': end_date.day
                    }
                }
                
                request_body = {
                    'filters': {
                        'dateFilter': {
                            'ranges': [date_range]
                        }
                    },
                    'pageSize': page_size
                }
                
                request = self.service.mediaItems().search(body=request_body)
                response = request.execute()
                
                media_items = response.get('mediaItems', [])
                logger.info(f"Found {len(media_items)} photos for {start_date.date()}")
                
                for item in media_items:
                    photos_found.append({
                        'item': item,
                        'date': start_date.date(),
                        'year_offset': year_offset
                    })
                    
            except Exception as e:
                logger.error(f"Error searching photos for {start_date.date()}: {e}")
        
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
                original_filename = item.get('filename', 'unknown')
                file_extension = original_filename.split('.')[-1].lower() if '.' in original_filename else 'jpg'
                filename = f"{date}_{item['id']}.{file_extension}"
                file_path = self.output_dir / filename
                
                # Skip if file already exists
                if skip_existing and file_path.exists():
                    logger.info(f"Skipping existing file: {filename}")
                    downloaded_files.append(file_path)
                    continue
                
                # Download the photo
                logger.info(f"Downloading: {filename}")
                
                # Get the download URL
                base_url = item.get('baseUrl', '')
                if not base_url:
                    logger.warning(f"No download URL for {filename}")
                    continue
                
                # Add parameters for original resolution
                download_url = base_url + '=d'
                
                response = requests.get(download_url, timeout=30)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_files.append(file_path)
                    logger.info(f"Successfully downloaded: {filename}")
                else:
                    logger.error(f"Failed to download {filename}: HTTP {response.status_code}")
                
            except Exception as e:
                logger.error(f"Failed to download {item.get('filename', 'unknown')}: {e}")
        
        return downloaded_files
    
    def fetch_and_download(
        self, 
        target_date: Optional[datetime] = None,
        years_back: int = 5,
        skip_existing: bool = True
    ) -> List[Path]:
        """Main method to fetch and download photos for a date."""
        if not self.authenticate():
            raise RuntimeError("Failed to authenticate with Google Photos")
        
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


def fetch_google_photos_airflow(
    target_date: Optional[str] = None,
    years_back: int = 5,
    output_dir: str = "./images",
    credentials_file: str = "creds.json",
    token_file: str = "token.pickle"
) -> None:
    """
    Airflow-compatible function to fetch photos from Google Photos.
    
    Args:
        target_date: Date string in YYYY-MM-DD format (defaults to today)
        years_back: Number of years to look back
        output_dir: Directory to save downloaded photos
        credentials_file: Path to Google OAuth credentials file
        token_file: Path to token file for persistent authentication
    """
    # Parse target date
    if target_date:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        parsed_date = datetime.now()
    
    # Create fetcher and download photos
    fetcher = GooglePhotosFetcher(
        credentials_file=credentials_file,
        token_file=token_file,
        output_dir=output_dir
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
    
    parser = argparse.ArgumentParser(description="Fetch Google Photos for a date")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--years-back", type=int, default=5)
    parser.add_argument("--output-dir", default="./images")
    parser.add_argument("--credentials", default="creds.json", help="Path to credentials file")
    parser.add_argument("--token", default="token.pickle", help="Path to token file")
    
    args = parser.parse_args()
    
    fetch_google_photos_airflow(
        target_date=args.date,
        years_back=args.years_back,
        output_dir=args.output_dir,
        credentials_file=args.credentials,
        token_file=args.token
    ) 