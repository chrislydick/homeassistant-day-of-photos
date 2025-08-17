#!/usr/bin/env python3
"""
Check account permissions and provide Azure app configuration guidance
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_account_permissions():
    """Check account permissions and provide guidance."""
    print("🔍 Account Permissions and Azure Configuration Check")
    print("=" * 70)
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing ONEDRIVE_CLIENT_ID or ONEDRIVE_CLIENT_SECRET")
        return
    
    print(f"✅ Using client ID: {client_id}")
    
    print("\n🔧 Azure App Registration Settings to Check:")
    print("=" * 60)
    
    print("1. OVERVIEW Tab:")
    print("   - Check 'Supported account types'")
    print("   - Should be: 'Accounts in any organizational directory and personal Microsoft accounts'")
    print("   - If it's 'Accounts in this organizational directory only', that might be the issue")
    print()
    
    print("2. API PERMISSIONS Tab:")
    print("   - Should have: Microsoft Graph → Files.Read.All")
    print("   - Status should be: 'Granted for [your organization]'")
    print("   - If it shows 'Granted for [your username]', that's the problem")
    print("   - Click 'Grant admin consent for [your organization]' if needed")
    print()
    
    print("3. TOKEN CONFIGURATION Tab:")
    print("   - Check if there are any token lifetime policies")
    print("   - These might be preventing refresh tokens")
    print()
    
    print("4. AUTHENTICATION Tab (you already checked):")
    print("   ✅ Web platform configured")
    print("   ✅ No implicit flows enabled")
    print()
    
    print("🚨 Most Likely Issues:")
    print("=" * 60)
    print("1. API permissions not granted for organization")
    print("2. Supported account types too restrictive")
    print("3. Token lifetime policies blocking refresh tokens")
    print("4. Conditional access policies")
    print()
    
    print("🔧 Quick Fixes to Try:")
    print("=" * 60)
    print("1. Grant admin consent:")
    print("   - Go to API permissions tab")
    print("   - Click 'Grant admin consent for [your organization]'")
    print("   - Wait a few minutes for propagation")
    print()
    print("2. Change supported account types:")
    print("   - Go to Overview tab")
    print("   - Change to 'Accounts in any organizational directory and personal Microsoft accounts'")
    print()
    print("3. Check conditional access:")
    print("   - Go to Azure AD → Conditional access")
    print("   - Ensure your account isn't blocked")
    print()
    
    print("🧪 Test After Changes:")
    print("=" * 60)
    print("After making changes, wait 5-10 minutes, then run:")
    print("python3 debug_token_exchange.py")
    print()
    print("You should see:")
    print("✅ Refresh token present: [some number] characters")

def test_current_permissions():
    """Test current permissions with a simple API call."""
    print("\n🧪 Testing Current Permissions")
    print("=" * 60)
    
    # First, let's get a fresh token to test with
    print("Getting a fresh token to test permissions...")
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    # Get authorization code
    auth_url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        f"client_id={client_id}&"
        "response_type=code&"
        "redirect_uri=http://localhost:8080&"
        "scope=Files.Read.All&"
        "response_mode=query"
    )
    
    print("Please visit this URL to get an authorization code:")
    print(auth_url)
    
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    # Exchange for token
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'http://localhost:8080'
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            
            print("✅ Got access token, testing permissions...")
            
            # Test different API endpoints
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test 1: Get user info
            try:
                user_response = requests.get(
                    'https://graph.microsoft.com/v1.0/me',
                    headers=headers,
                    timeout=10
                )
                print(f"   User info: {'✅' if user_response.status_code == 200 else '❌'} ({user_response.status_code})")
            except Exception as e:
                print(f"   User info: ❌ Error: {e}")
            
            # Test 2: Get drive info
            try:
                drive_response = requests.get(
                    'https://graph.microsoft.com/v1.0/me/drive',
                    headers=headers,
                    timeout=10
                )
                print(f"   Drive info: {'✅' if drive_response.status_code == 200 else '❌'} ({drive_response.status_code})")
            except Exception as e:
                print(f"   Drive info: ❌ Error: {e}")
            
            # Test 3: List files (this requires Files.Read.All)
            try:
                files_response = requests.get(
                    'https://graph.microsoft.com/v1.0/me/drive/root/children',
                    headers=headers,
                    timeout=10
                )
                print(f"   Files access: {'✅' if files_response.status_code == 200 else '❌'} ({files_response.status_code})")
            except Exception as e:
                print(f"   Files access: ❌ Error: {e}")
            
        else:
            print(f"❌ Failed to get token: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing permissions: {e}")

if __name__ == "__main__":
    check_account_permissions()
    test_current_permissions()
