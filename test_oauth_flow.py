#!/usr/bin/env python3
"""
Test OAuth flow to see what tokens are being returned
"""

import os
import requests
import webbrowser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oauth_flow():
    """Test the complete OAuth flow and see what tokens we get."""
    print("🔍 Testing OAuth Flow")
    print("=" * 50)
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing ONEDRIVE_CLIENT_ID or ONEDRIVE_CLIENT_SECRET")
        return
    
    print(f"✅ Using client ID: {client_id[:10]}...")
    
    # Step 1: Get authorization URL
    auth_url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        f"client_id={client_id}&"
        "response_type=code&"
        "redirect_uri=http://localhost:8080&"
        "scope=Files.Read.All offline_access&"  # Added offline_access for refresh tokens
        "response_mode=query"
    )
    
    print("\n🔐 Authorization URL:")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    
    print("\n📋 Important: Notice the 'offline_access' scope in the URL")
    print("This scope is required for refresh tokens!")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened automatically")
    except:
        print("⚠️ Could not open browser automatically")
    
    print("\nWaiting for authorization code...")
    auth_code = input("Enter the authorization code from the URL: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    # Step 2: Exchange authorization code for tokens
    print("\n🔄 Exchanging authorization code for tokens...")
    
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'http://localhost:8080'
    }
    
    response = requests.post(token_url, data=data, timeout=10)
    
    print(f"Token response status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        
        print("\n✅ Token Response Analysis:")
        print("=" * 50)
        print(f"Keys in response: {list(token_data.keys())}")
        
        if 'access_token' in token_data:
            print(f"✅ Access token: {len(token_data['access_token'])} characters")
        else:
            print("❌ No access token in response")
        
        if 'refresh_token' in token_data:
            refresh_token = token_data['refresh_token']
            if refresh_token:
                print(f"✅ Refresh token: {len(refresh_token)} characters")
            else:
                print("❌ Refresh token is None")
        else:
            print("❌ No refresh_token key in response")
        
        if 'expires_in' in token_data:
            print(f"✅ Token expires in: {token_data['expires_in']} seconds ({token_data['expires_in']/3600:.1f} hours)")
        
        if 'token_type' in token_data:
            print(f"✅ Token type: {token_data['token_type']}")
        
        # Test the access token
        print("\n🧪 Testing access token...")
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'Content-Type': 'application/json'
        }
        
        test_response = requests.get(
            'https://graph.microsoft.com/v1.0/me/drive',
            headers=headers,
            timeout=10
        )
        
        if test_response.status_code == 200:
            print("✅ Access token works correctly")
            drive_info = test_response.json()
            print(f"   Drive type: {drive_info.get('driveType', 'Unknown')}")
        else:
            print(f"❌ Access token test failed: {test_response.status_code}")
            print(f"   Response: {test_response.text}")
        
        # Test refresh token if available
        if 'refresh_token' in token_data and token_data['refresh_token']:
            print("\n🔄 Testing refresh token...")
            
            refresh_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': token_data['refresh_token']
            }
            
            refresh_response = requests.post(token_url, data=refresh_data, timeout=10)
            
            if refresh_response.status_code == 200:
                new_tokens = refresh_response.json()
                print("✅ Refresh token works correctly")
                print(f"   New access token: {len(new_tokens['access_token'])} characters")
                if 'refresh_token' in new_tokens:
                    print(f"   New refresh token: {len(new_tokens['refresh_token'])} characters")
            else:
                print(f"❌ Refresh token test failed: {refresh_response.status_code}")
                print(f"   Response: {refresh_response.text}")
        
        print("\n💡 Recommendations:")
        print("=" * 50)
        if 'refresh_token' in token_data and token_data['refresh_token']:
            print("✅ Your OAuth flow is working correctly!")
            print("   The issue might be in how the token is being saved.")
        else:
            print("❌ No refresh token received.")
            print("   Check your Azure app configuration:")
            print("   1. Ensure 'offline_access' scope is included")
            print("   2. Make sure you're using authorization code flow (not implicit)")
            print("   3. Verify redirect URI is exactly: http://localhost:8080")
    
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_oauth_flow()
