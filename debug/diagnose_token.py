#!/usr/bin/env python3
"""
Diagnostic script to check OneDrive token expiration and identify issues
"""

import os
import pickle
import requests
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_token_file():
    """Check if token file exists and is valid."""
    token_file = Path("./onedrive_token.pickle")
    
    print("🔍 Token File Analysis")
    print("=" * 50)
    
    if not token_file.exists():
        print("❌ Token file does not exist")
        return None
    
    print(f"✅ Token file exists: {token_file}")
    print(f"📁 File size: {token_file.stat().st_size} bytes")
    print(f"📅 Last modified: {datetime.fromtimestamp(token_file.stat().st_mtime)}")
    
    try:
        with open(token_file, 'rb') as f:
            token_data = pickle.load(f)
        
        print(f"✅ Token file loaded successfully")
        print(f"📋 Token keys: {list(token_data.keys())}")
        
        return token_data
        
    except Exception as e:
        print(f"❌ Failed to load token file: {e}")
        return None

def analyze_token(token_data):
    """Analyze token data for expiration info."""
    if not token_data:
        return
    
    print("\n🔍 Token Analysis")
    print("=" * 50)
    
    # Check for access token
    if 'access_token' in token_data:
        access_token = token_data['access_token']
        print(f"✅ Access token present: {len(access_token)} characters")
        
        # Try to decode JWT token to check expiration
        try:
            import jwt
            # Note: Microsoft tokens might not be standard JWT format
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            if 'exp' in decoded:
                exp_timestamp = decoded['exp']
                exp_date = datetime.fromtimestamp(exp_timestamp)
                now = datetime.now()
                time_until_expiry = exp_date - now
                
                print(f"📅 Token expires at: {exp_date}")
                print(f"⏰ Time until expiry: {time_until_expiry}")
                print(f"🔄 Token age: {now - datetime.fromtimestamp(decoded.get('iat', exp_timestamp))}")
                
                if time_until_expiry.total_seconds() < 0:
                    print("❌ Token is expired!")
                elif time_until_expiry.total_seconds() < 3600:  # Less than 1 hour
                    print("⚠️ Token expires soon (less than 1 hour)")
                else:
                    print("✅ Token is valid")
            else:
                print("⚠️ Token decoded but no expiration found")
                    
        except ImportError:
            print("⚠️ JWT library not available, cannot decode token")
        except Exception as e:
            print(f"⚠️ Could not decode token (this is normal for Microsoft tokens): {e}")
            print("💡 Microsoft Graph API tokens often use non-standard JWT format")
            print("💡 The token validity test below will show if it's actually working")
    
    # Check for refresh token
    if 'refresh_token' in token_data:
        refresh_token = token_data['refresh_token']
        if refresh_token is not None:
            print(f"✅ Refresh token present: {len(refresh_token)} characters")
        else:
            print("⚠️ Refresh token is None")
    else:
        print("❌ No refresh token found")

def test_token_validity(token_data):
    """Test if the token is currently valid."""
    if not token_data or 'access_token' not in token_data:
        return
    
    print("\n🧪 Token Validity Test")
    print("=" * 50)
    
    access_token = token_data['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me/drive',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Token is valid - API call successful")
            drive_info = response.json()
            print(f"📁 Drive type: {drive_info.get('driveType', 'Unknown')}")
            print(f"💾 Total space: {drive_info.get('quota', {}).get('total', 'Unknown')} bytes")
        elif response.status_code == 401:
            print("❌ Token is invalid - Unauthorized")
            error_data = response.json()
            print(f"🔍 Error details: {error_data}")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"🔍 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")

def check_environment():
    """Check environment configuration."""
    print("\n🔍 Environment Check")
    print("=" * 50)
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if client_id:
        print(f"✅ ONEDRIVE_CLIENT_ID: {client_id[:10]}...")
    else:
        print("❌ ONEDRIVE_CLIENT_ID not set")
    
    if client_secret:
        print(f"✅ ONEDRIVE_CLIENT_SECRET: {client_secret[:10]}...")
    else:
        print("❌ ONEDRIVE_CLIENT_SECRET not set")

def main():
    """Main diagnostic function."""
    print("🔍 OneDrive Token Diagnostic")
    print("=" * 60)
    
    # Check environment
    check_environment()
    
    # Check token file
    token_data = check_token_file()
    
    # Analyze token
    analyze_token(token_data)
    
    # Test token validity
    test_token_validity(token_data)
    
    print("\n💡 Recommendations:")
    print("=" * 50)
    print("1. If token expires quickly, check your Azure app configuration")
    print("2. Ensure 'Files.Read.All' permission is granted")
    print("3. Check if conditional access policies are affecting your account")
    print("4. Verify the app registration has proper token lifetime settings")
    print("5. Consider using a service account for automation")

if __name__ == "__main__":
    main()
