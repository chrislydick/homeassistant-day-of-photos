#!/usr/bin/env python3
"""
Comprehensive token debugging script for OneDrive authentication issues
"""

import os
import pickle
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_token_lifecycle():
    """Test the complete token lifecycle to identify issues."""
    print("🔍 OneDrive Token Lifecycle Debug")
    print("=" * 60)
    
    # Check environment
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing ONEDRIVE_CLIENT_ID or ONEDRIVE_CLIENT_SECRET")
        return
    
    print(f"✅ Environment variables found")
    print(f"   Client ID: {client_id[:10]}...")
    print(f"   Client Secret: {client_secret[:10]}...")
    
    # Check token file
    token_file = Path("./onedrive_token.pickle")
    print(f"\n📁 Token file: {token_file.absolute()}")
    
    if not token_file.exists():
        print("❌ Token file does not exist")
        print("💡 This means you need to authenticate manually each time")
        return
    
    print(f"✅ Token file exists")
    print(f"   Size: {token_file.stat().st_size} bytes")
    print(f"   Modified: {datetime.fromtimestamp(token_file.stat().st_mtime)}")
    
    # Load and analyze token
    try:
        with open(token_file, 'rb') as f:
            token_data = pickle.load(f)
        
        print(f"\n🔍 Token Analysis:")
        print(f"   Keys: {list(token_data.keys())}")
        
        if 'access_token' in token_data:
            access_token = token_data['access_token']
            print(f"   Access token: {len(access_token)} characters")
            
            # Try to decode JWT
            try:
                import jwt
                decoded = jwt.decode(access_token, options={"verify_signature": False})
                print(f"   JWT decoded successfully")
                
                if 'exp' in decoded:
                    exp_timestamp = decoded['exp']
                    exp_date = datetime.fromtimestamp(exp_timestamp)
                    now = datetime.now()
                    time_until_expiry = exp_date - now
                    
                    print(f"   Expires at: {exp_date}")
                    print(f"   Time until expiry: {time_until_expiry}")
                    
                    if time_until_expiry.total_seconds() < 0:
                        print("   ❌ Token is expired!")
                    elif time_until_expiry.total_seconds() < 3600:
                        print("   ⚠️ Token expires soon (< 1 hour)")
                    else:
                        print("   ✅ Token is valid")
                        
            except Exception as e:
                print(f"   ⚠️ Could not decode JWT: {e}")
        
        if 'refresh_token' in token_data:
            refresh_token = token_data['refresh_token']
            if refresh_token:
                print(f"   Refresh token: {len(refresh_token)} characters")
            else:
                print(f"   ❌ Refresh token is None")
        else:
            print(f"   ❌ No refresh token found")
        
        # Test current token
        print(f"\n🧪 Testing Current Token:")
        if 'access_token' in token_data:
            headers = {
                'Authorization': f'Bearer {token_data["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            try:
                response = requests.get(
                    'https://graph.microsoft.com/v1.0/me/drive',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("   ✅ Token is currently valid")
                    drive_info = response.json()
                    print(f"   Drive type: {drive_info.get('driveType', 'Unknown')}")
                elif response.status_code == 401:
                    print("   ❌ Token is invalid (401 Unauthorized)")
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                else:
                    print(f"   ⚠️ Unexpected response: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing token: {e}")
        
        # Test refresh token
        print(f"\n🔄 Testing Refresh Token:")
        if 'refresh_token' in token_data and token_data['refresh_token']:
            refresh_token = token_data['refresh_token']
            
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            try:
                response = requests.post(token_url, data=data, timeout=10)
                
                if response.status_code == 200:
                    new_token_data = response.json()
                    print("   ✅ Refresh token is valid")
                    print(f"   New access token: {len(new_token_data['access_token'])} characters")
                    
                    if 'refresh_token' in new_token_data:
                        print(f"   New refresh token: {len(new_token_data['refresh_token'])} characters")
                    else:
                        print(f"   ⚠️ No new refresh token in response")
                        
                elif response.status_code == 400:
                    error_data = response.json()
                    print(f"   ❌ Refresh token is invalid: {error_data}")
                else:
                    print(f"   ⚠️ Unexpected refresh response: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error testing refresh: {e}")
        else:
            print("   ❌ No refresh token to test")
    
    except Exception as e:
        print(f"❌ Error loading token: {e}")

def check_azure_app_config():
    """Provide guidance on Azure app configuration."""
    print(f"\n🔧 Azure App Configuration Recommendations:")
    print("=" * 60)
    print("1. Check your Azure app registration settings:")
    print("   - Go to Azure Portal > App registrations > Your app")
    print("   - Check 'Authentication' settings")
    print("   - Verify redirect URI: http://localhost:8080")
    print("   - Ensure 'Files.Read.All' permission is granted")
    print()
    print("2. Check token lifetime policies:")
    print("   - Go to Azure Portal > Azure Active Directory > Token lifetime policies")
    print("   - Default access token lifetime is 1 hour")
    print("   - Refresh tokens can last up to 90 days")
    print()
    print("3. Check conditional access policies:")
    print("   - Go to Azure Portal > Azure Active Directory > Conditional access")
    print("   - Ensure your account isn't blocked by policies")
    print()
    print("4. Consider using a service account:")
    print("   - Create a dedicated service account for automation")
    print("   - Grant it minimal required permissions")
    print("   - Use it instead of your personal account")

def main():
    """Main diagnostic function."""
    check_token_lifecycle()
    check_azure_app_config()
    
    print(f"\n💡 Quick Fixes:")
    print("=" * 60)
    print("1. If token expires quickly (< 24 hours):")
    print("   - This is normal for Microsoft Graph API")
    print("   - The script should use refresh tokens automatically")
    print("   - Check if refresh token mechanism is working")
    print()
    print("2. If you need to re-authenticate frequently:")
    print("   - Check if refresh token is being saved properly")
    print("   - Verify refresh token isn't being invalidated")
    print("   - Check Azure app configuration")
    print()
    print("3. For production use:")
    print("   - Consider using Microsoft Graph SDK")
    print("   - Implement proper token caching")
    print("   - Use service accounts for automation")

if __name__ == "__main__":
    main()
