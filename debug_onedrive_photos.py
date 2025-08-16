#!/usr/bin/env python3
"""
Debug version of OneDrive Photos Script

This script helps debug why photos aren't being found by showing:
- What folders exist in OneDrive
- What files are found in each folder
- Date extraction attempts
- Authentication status
"""

import logging
import os
import pickle
import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import webbrowser
import time
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_onedrive.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OneDrivePhotosDebugger:
    """Debug version of OneDrive photos fetcher."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_file: str = "./onedrive_token.pickle",
        photos_folder: str = "Pictures"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = Path(token_file)
        self.photos_folder = photos_folder
        self.access_token = None
        self.refresh_token = None
        
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
                        logger.info("✅ Loaded existing valid OneDrive token")
                        return True
                    else:
                        logger.warning("⚠️ Token is invalid or expired, trying refresh")
                        return self._refresh_token()
                else:
                    logger.warning("⚠️ Token file is empty or invalid")
                    return False
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to load token: {e}")
                return False
        return False
    
    def _save_token(self, token_data: dict) -> None:
        """Save token for future use."""
        try:
            with open(self.token_file, 'wb') as f:
                pickle.dump(token_data, f)
            logger.info("✅ Saved OneDrive authentication token")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save token: {e}")
    
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
            logger.warning(f"⚠️ Token test failed: {e}")
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
                
                logger.info("✅ Successfully refreshed OneDrive token")
                return True
            else:
                logger.error(f"❌ Token refresh failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
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
                logger.error("❌ No authorization code provided")
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
                
                logger.info("✅ Successfully authenticated with OneDrive")
                return True
            else:
                logger.error(f"❌ Token exchange failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    def _get_photo_date(self, file_item) -> Optional[datetime]:
        """Extract date from photo file using multiple methods."""
        try:
            filename = file_item['name']
            logger.info(f"🔍 Analyzing file: {filename}")
            
            # Method 1: Try to get date from filename patterns
            filename_stem = Path(filename).stem.lower()
            
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
                match = re.search(pattern, filename_stem)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        if len(groups[0]) == 4:  # YYYY-MM-DD or YYYY_MM_DD or YYYYMMDD
                            year, month, day = groups
                        else:  # MM-DD-YYYY or MM_DD_YYYY
                            month, day, year = groups
                        date = datetime(int(year), int(month), int(day))
                        logger.info(f"✅ Found date in filename: {date.date()}")
                        return date
            
            # Method 2: Use file creation time from OneDrive metadata
            if 'createdDateTime' in file_item:
                date = datetime.fromisoformat(file_item['createdDateTime'].replace('Z', '+00:00'))
                logger.info(f"✅ Using creation date: {date.date()}")
                return date
            
            # Method 3: Use file modification time
            if 'lastModifiedDateTime' in file_item:
                date = datetime.fromisoformat(file_item['lastModifiedDateTime'].replace('Z', '+00:00'))
                logger.info(f"✅ Using modification date: {date.date()}")
                return date
            
            logger.warning(f"⚠️ Could not extract date from {filename}")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting date from {file_item['name']}: {e}")
            return None
    
    def debug_onedrive_structure(self):
        """Debug OneDrive structure to understand what's available."""
        if not self.authenticate():
            logger.error("❌ Failed to authenticate")
            return
        
        logger.info("🔍 Starting OneDrive structure debug...")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # First, let's see what's in the root
            logger.info("📁 Checking root directory...")
            root_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
            response = requests.get(root_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                root_items = response.json().get('value', [])
                logger.info(f"📋 Found {len(root_items)} items in root:")
                
                for item in root_items:
                    item_type = "📁 Folder" if item.get('folder') else "📄 File"
                    logger.info(f"  {item_type}: {item['name']}")
                    
                    # If it's the Pictures folder, explore it
                    if item.get('folder') and item['name'].lower() in ['pictures', 'photos', 'camera roll']:
                        logger.info(f"🔍 Exploring folder: {item['name']}")
                        self._explore_folder(item['id'], item['name'], headers, depth=1)
            else:
                logger.error(f"❌ Failed to get root items: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error debugging OneDrive structure: {e}")
    
    def _explore_folder(self, folder_id: str, folder_name: str, headers: dict, depth: int = 0):
        """Recursively explore a folder to find photos."""
        indent = "  " * depth
        
        try:
            folder_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            response = requests.get(folder_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                items = response.json().get('value', [])
                logger.info(f"{indent}📁 {folder_name}: {len(items)} items")
                
                photo_count = 0
                folder_count = 0
                
                for item in items:
                    if item.get('folder'):
                        folder_count += 1
                        logger.info(f"{indent}  📁 {item['name']}")
                        
                        # Recursively explore subfolders (limit depth to avoid infinite recursion)
                        if depth < 3:
                            self._explore_folder(item['id'], item['name'], headers, depth + 1)
                    elif item.get('file'):
                        file_extension = Path(item['name']).suffix.lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef']:
                            photo_count += 1
                            photo_date = self._get_photo_date(item)
                            date_str = f" ({photo_date.date()})" if photo_date else " (no date)"
                            logger.info(f"{indent}  📸 {item['name']}{date_str}")
                
                logger.info(f"{indent}📊 Summary for {folder_name}: {photo_count} photos, {folder_count} folders")
            else:
                logger.error(f"{indent}❌ Failed to get items from {folder_name}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"{indent}❌ Error exploring {folder_name}: {e}")


def main():
    """Main debug function."""
    # Get credentials from environment variables
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.error("❌ ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET must be set in environment variables")
        sys.exit(1)
    
    logger.info("🚀 Starting OneDrive Photos Debugger")
    
    # Create debugger and explore OneDrive structure
    debugger = OneDrivePhotosDebugger(
        client_id=client_id,
        client_secret=client_secret,
        token_file="./onedrive_token.pickle",
        photos_folder="Pictures"
    )
    
    debugger.debug_onedrive_structure()
    
    logger.info("✅ Debug completed. Check debug_onedrive.log for details.")


if __name__ == "__main__":
    main()
