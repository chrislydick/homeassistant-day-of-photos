"""
Enhanced iCloud Photo Fetcher for Airflow

This module provides a robust way to fetch photos from iCloud with improved
2FA handling and session management. It's designed to work seamlessly with
Apache Airflow for daily execution.
"""

from __future__ import annotations

import logging
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

try:
    from pyicloud import PyiCloudService  # type: ignore
except ImportError:
    PyiCloudService = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class iCloudPhotoFetcher:
    """Enhanced iCloud photo fetcher with improved 2FA handling."""
    
    def __init__(
        self,
        username: str,
        password: str,
        session_file: str = "icloud_session.pickle",
        output_dir: str = "./images"
    ):
        self.username = username
        self.password = password
        self.session_file = Path(session_file)
        self.output_dir = Path(output_dir)
        self.api: Optional[PyiCloudService] = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_session(self) -> bool:
        """Load existing session if available."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'rb') as f:
                    session_data = pickle.load(f)
                    self.api = PyiCloudService(
                        self.username, 
                        self.password, 
                        session_data=session_data
                    )
                logger.info("Loaded existing iCloud session")
                return True
            except Exception as e:
                logger.warning(f"Failed to load session: {e}")
                return False
        return False
    
    def _save_session(self) -> None:
        """Save current session for future use."""
        if self.api and hasattr(self.api, 'session'):
            try:
                with open(self.session_file, 'wb') as f:
                    pickle.dump(self.api.session, f)
                logger.info("Saved iCloud session")
            except Exception as e:
                logger.warning(f"Failed to save session: {e}")
    
    def _handle_2fa(self) -> bool:
        """Handle two-factor authentication with improved error handling."""
        if not self.api or not self.api.requires_2sa:
            return True
            
        logger.info("Two-factor authentication required")
        
        # Try to get 2FA code from environment
        code = os.environ.get("ICLOUD_2FA_CODE")
        device_index = int(os.environ.get("ICLOUD_2FA_DEVICE", "0"))
        
        if not code:
            logger.error("No 2FA code provided. Set ICLOUD_2FA_CODE environment variable")
            return False
        
        try:
            devices = self.api.trusted_devices
            
            if not devices:
                # Handle case where no devices are returned
                logger.info("No trusted devices found, trying manual verification")
                if not self.api.validate_verification_code(None, code):
                    logger.error("Failed to validate 2FA code")
                    return False
            else:
                # Use specific device
                if device_index < 0 or device_index >= len(devices):
                    logger.error(f"Invalid device index {device_index}. Available devices: {len(devices)}")
                    return False
                
                device = devices[device_index]
                logger.info(f"Using device: {device.get('deviceName', 'Unknown')}")
                
                if not self.api.send_verification_code(device):
                    logger.error("Failed to send verification code")
                    return False
                    
                if not self.api.validate_verification_code(device, code):
                    logger.error("Failed to validate 2FA code")
                    return False
            
            # Trust the session
            try:
                self.api.trust_session()
                logger.info("Successfully authenticated with 2FA")
            except Exception as e:
                logger.warning(f"Failed to trust session: {e}")
                
            return True
            
        except Exception as e:
            logger.error(f"2FA authentication failed: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Authenticate with iCloud, handling 2FA if needed."""
        if PyiCloudService is None:
            logger.error("pyicloud-ipd is not installed")
            return False
        
        # Try to load existing session first
        if self._load_session():
            try:
                # Test if session is still valid
                self.api.photos.all
                logger.info("Using existing valid session")
                return True
            except Exception:
                logger.info("Existing session expired, re-authenticating")
        
        # Create new session
        try:
            self.api = PyiCloudService(self.username, self.password)
            
            if self.api.requires_2sa:
                if not self._handle_2fa():
                    return False
            
            # Test authentication
            self.api.photos.all
            logger.info("Successfully authenticated with iCloud")
            
            # Save session for future use
            self._save_session()
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def fetch_photos_for_date(
        self, 
        target_date: datetime, 
        years_back: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch photos for a specific date across multiple years."""
        if not self.api:
            logger.error("Not authenticated")
            return []
        
        photos_found = []
        
        for year_offset in range(1, years_back + 1):
            past_date = target_date.replace(year=target_date.year - year_offset)
            start_date = past_date
            end_date = past_date + timedelta(days=1)
            
            logger.info(f"Searching for photos on {past_date.date()}")
            
            try:
                photos = self.api.photos.search(start_date=start_date, end_date=end_date)
                photo_list = list(photos)
                logger.info(f"Found {len(photo_list)} photos for {past_date.date()}")
                
                for photo in photo_list:
                    photos_found.append({
                        'photo': photo,
                        'date': past_date.date(),
                        'year_offset': year_offset
                    })
                    
            except Exception as e:
                logger.error(f"Error searching photos for {past_date.date()}: {e}")
        
        return photos_found
    
    def download_photos(
        self, 
        photos_data: List[Dict[str, Any]], 
        skip_existing: bool = True
    ) -> List[Path]:
        """Download photos to local directory."""
        downloaded_files = []
        
        for photo_data in photos_data:
            photo = photo_data['photo']
            date = photo_data['date']
            
            try:
                # Create filename with date prefix for organization
                file_extension = photo.filename.split('.')[-1].lower()
                filename = f"{date}_{photo.id}.{file_extension}"
                file_path = self.output_dir / filename
                
                # Skip if file already exists
                if skip_existing and file_path.exists():
                    logger.info(f"Skipping existing file: {filename}")
                    downloaded_files.append(file_path)
                    continue
                
                # Download the photo
                logger.info(f"Downloading: {filename}")
                asset = photo.download()
                asset.save(file_path)
                
                downloaded_files.append(file_path)
                logger.info(f"Successfully downloaded: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to download {photo.filename}: {e}")
        
        return downloaded_files
    
    def fetch_and_download(
        self, 
        target_date: Optional[datetime] = None,
        years_back: int = 5,
        skip_existing: bool = True
    ) -> List[Path]:
        """Main method to fetch and download photos for a date."""
        if not self.authenticate():
            raise RuntimeError("Failed to authenticate with iCloud")
        
        if target_date is None:
            target_date = datetime.now()
        
        logger.info(f"Fetching photos for {target_date.date()} going back {years_back} years")
        
        # Fetch photos
        photos_data = self.fetch_photos_for_date(target_date, years_back)
        
        if not photos_data:
            logger.info("No photos found")
            return []
        
        # Download photos
        downloaded_files = self.download_photos(photos_data, skip_existing)
        
        logger.info(f"Downloaded {len(downloaded_files)} photos to {self.output_dir}")
        return downloaded_files


def fetch_photos_airflow(
    target_date: Optional[str] = None,
    years_back: int = 5,
    output_dir: str = "./images",
    username: Optional[str] = None,
    password: Optional[str] = None,
    session_file: str = "icloud_session.pickle"
) -> None:
    """
    Airflow-compatible function to fetch photos from iCloud.
    
    Args:
        target_date: Date string in YYYY-MM-DD format (defaults to today)
        years_back: Number of years to look back
        output_dir: Directory to save downloaded photos
        username: iCloud username (from Airflow variables)
        password: iCloud app-specific password (from Airflow variables)
        session_file: Path to session file for persistent authentication
    """
    if not username or not password:
        raise ValueError("Username and password must be provided")
    
    # Parse target date
    if target_date:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        parsed_date = datetime.now()
    
    # Create fetcher and download photos
    fetcher = iCloudPhotoFetcher(
        username=username,
        password=password,
        session_file=session_file,
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
    
    parser = argparse.ArgumentParser(description="Fetch iCloud photos for a date")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--years-back", type=int, default=5)
    parser.add_argument("--output-dir", default="./images")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    
    args = parser.parse_args()
    
    fetch_photos_airflow(
        target_date=args.date,
        years_back=args.years_back,
        output_dir=args.output_dir,
        username=args.username,
        password=args.password
    ) 