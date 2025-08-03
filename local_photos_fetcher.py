"""
Local Photos Fetcher for Airflow

This module provides a robust way to fetch "on this day" photos from your local
photo library. It works with any organized photo directory structure and avoids
all cloud sync and 2FA issues.
"""

from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalPhotosFetcher:
    """Local photos fetcher that works with organized photo directories."""
    
    def __init__(
        self,
        source_dir: str,
        output_dir: str = "./images",
        date_format: str = "YYYY-MM-DD",
        file_patterns: Optional[List[str]] = None
    ):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.date_format = date_format
        
        # Default file patterns for photos
        if file_patterns is None:
            file_patterns = [
                "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff", 
                "*.heic", "*.heif", "*.webp", "*.raw", "*.cr2", "*.nef"
            ]
        self.file_patterns = file_patterns
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {self.source_dir}")
    
    def _get_photo_date(self, file_path: Path) -> Optional[datetime]:
        """Extract date from photo file using multiple methods."""
        try:
            # Method 1: Try to get date from EXIF data
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                
                with Image.open(file_path) as img:
                    exif = img._getexif()
                    if exif:
                        for tag_id in exif:
                            tag = TAGS.get(tag_id, tag_id)
                            data = exif[tag_id]
                            if tag == "DateTimeOriginal":
                                return datetime.strptime(data, "%Y:%m:%d %H:%M:%S")
                            elif tag == "DateTime":
                                return datetime.strptime(data, "%Y:%m:%d %H:%M:%S")
            except Exception:
                pass
            
            # Method 2: Try to get date from filename patterns
            filename = file_path.stem.lower()
            
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
            
            # Method 3: Use file modification time as fallback
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime)
            
        except Exception as e:
            logger.warning(f"Could not extract date from {file_path}: {e}")
            return None
    
    def _find_photos_by_date(
        self, 
        target_date: datetime, 
        years_back: int = 5
    ) -> List[Dict[str, Any]]:
        """Find photos from the same day across multiple years."""
        photos_found = []
        month_day = (target_date.month, target_date.day)
        
        logger.info(f"Searching for photos on {target_date.date()} going back {years_back} years")
        
        for year_offset in range(1, years_back + 1):
            past_year = target_date.year - year_offset
            search_date = datetime(past_year, month_day[0], month_day[1])
            
            logger.info(f"Searching for photos on {search_date.date()}")
            
            # Search through all subdirectories
            for file_path in self.source_dir.rglob("*"):
                if file_path.is_file() and any(file_path.match(pattern) for pattern in self.file_patterns):
                    photo_date = self._get_photo_date(file_path)
                    
                    if photo_date and photo_date.date() == search_date.date():
                        photos_found.append({
                            'file_path': file_path,
                            'date': search_date.date(),
                            'year_offset': year_offset,
                            'photo_date': photo_date
                        })
            
            logger.info(f"Found {len([p for p in photos_found if p['date'] == search_date.date()])} photos for {search_date.date()}")
        
        return photos_found
    
    def copy_photos(
        self, 
        photos_data: List[Dict[str, Any]], 
        skip_existing: bool = True
    ) -> List[Path]:
        """Copy photos to output directory."""
        copied_files = []
        
        for photo_data in photos_data:
            source_path = photo_data['file_path']
            date = photo_data['date']
            
            try:
                # Create filename with date prefix for organization
                file_extension = source_path.suffix.lower()
                filename = f"{date}_{source_path.stem}{file_extension}"
                dest_path = self.output_dir / filename
                
                # Skip if file already exists
                if skip_existing and dest_path.exists():
                    logger.info(f"Skipping existing file: {filename}")
                    copied_files.append(dest_path)
                    continue
                
                # Copy the photo
                logger.info(f"Copying: {filename}")
                shutil.copy2(source_path, dest_path)
                
                copied_files.append(dest_path)
                logger.info(f"Successfully copied: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to copy {source_path.name}: {e}")
        
        return copied_files
    
    def fetch_and_copy(
        self, 
        target_date: Optional[datetime] = None,
        years_back: int = 5,
        skip_existing: bool = True
    ) -> List[Path]:
        """Main method to find and copy photos for a date."""
        if target_date is None:
            target_date = datetime.now()
        
        logger.info(f"Fetching photos for {target_date.date()} going back {years_back} years")
        
        # Find photos
        photos_data = self._find_photos_by_date(target_date, years_back)
        
        if not photos_data:
            logger.info("No photos found")
            return []
        
        # Copy photos
        copied_files = self.copy_photos(photos_data, skip_existing)
        
        logger.info(f"Copied {len(copied_files)} photos to {self.output_dir}")
        return copied_files


def fetch_local_photos_airflow(
    target_date: Optional[str] = None,
    years_back: int = 5,
    source_dir: str = "/path/to/your/photos",
    output_dir: str = "./images",
    date_format: str = "YYYY-MM-DD"
) -> None:
    """
    Airflow-compatible function to fetch photos from local directory.
    
    Args:
        target_date: Date string in YYYY-MM-DD format (defaults to today)
        years_back: Number of years to look back
        source_dir: Directory containing your photo library
        output_dir: Directory to save copied photos
        date_format: Expected date format in filenames
    """
    # Parse target date
    if target_date:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d")
    else:
        parsed_date = datetime.now()
    
    # Create fetcher and copy photos
    fetcher = LocalPhotosFetcher(
        source_dir=source_dir,
        output_dir=output_dir,
        date_format=date_format
    )
    
    copied_files = fetcher.fetch_and_copy(
        target_date=parsed_date,
        years_back=years_back,
        skip_existing=True
    )
    
    logger.info(f"Airflow task completed. Copied {len(copied_files)} photos")


if __name__ == "__main__":
    # For testing outside of Airflow
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch local photos for a date")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--years-back", type=int, default=5)
    parser.add_argument("--source-dir", required=True, help="Source photo directory")
    parser.add_argument("--output-dir", default="./images", help="Output directory")
    parser.add_argument("--date-format", default="YYYY-MM-DD", help="Date format in filenames")
    
    args = parser.parse_args()
    
    fetch_local_photos_airflow(
        target_date=args.date,
        years_back=args.years_back,
        source_dir=args.source_dir,
        output_dir=args.output_dir,
        date_format=args.date_format
    ) 