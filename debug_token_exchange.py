#!/usr/bin/env python3
"""
Debug token exchange to see exactly what's happening
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_token_exchange():
    """Debug the token exchange process step by step."""
    print("🔍 Debugging Token Exchange")
    print("=" * 60)
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing ONEDRIVE_CLIENT_ID or ONEDRIVE_CLIENT_SECRET")
        return
    
    print(f"✅ Using client ID: {client_id}")
    print(f"✅ Using client secret: {client_secret[:10]}...")
    
    # Get authorization code
    print("\n🔐 Step 1: Get Authorization Code")
    print("=" * 50)
    
    auth_url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        f"client_id={client_id}&"
        "response_type=code&"
        "redirect_uri=http://localhost:8080&"
        "scope=Files.Read.All offline_access&"
        "response_mode=query"
    )
    
    print("Authorization URL:")
    print(auth_url)
    print()
    print("Please visit this URL in your browser and get the authorization code.")
    print("The code will be in the redirect URL like: http://localhost:8080?code=ABC123...")
    
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    print(f"✅ Authorization code received: {auth_code[:20]}...")
    
    # Exchange for tokens
    print("\n🔄 Step 2: Exchange Authorization Code for Tokens")
    print("=" * 50)
    
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    # Prepare the request data
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'http://localhost:8080'
    }
    
    print("Token exchange request data:")
    for key, value in data.items():
        if key == 'client_secret':
            print(f"  {key}: {value[:10]}...")
        elif key == 'code':
            print(f"  {key}: {value[:20]}...")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nMaking POST request to: {token_url}")
    
    # Make the request
    try:
        response = requests.post(token_url, data=data, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            
            # Analyze the response
            print(f"\n🔍 Response Analysis:")
            print("=" * 50)
            
            if 'access_token' in response_json:
                print(f"✅ Access token present: {len(response_json['access_token'])} characters")
            else:
                print("❌ No access token in response")
            
            if 'refresh_token' in response_json:
                refresh_token = response_json['refresh_token']
                if refresh_token:
                    print(f"✅ Refresh token present: {len(refresh_token)} characters")
                else:
                    print("❌ Refresh token is None")
            else:
                print("❌ No refresh_token key in response")
            
            if 'expires_in' in response_json:
                print(f"✅ Token expires in: {response_json['expires_in']} seconds")
            
            if 'token_type' in response_json:
                print(f"✅ Token type: {response_json['token_type']}")
            
            if 'error' in response_json:
                print(f"❌ Error in response: {response_json['error']}")
                if 'error_description' in response_json:
                    print(f"   Description: {response_json['error_description']}")
            
            # Check for specific error codes
            if response.status_code == 400:
                print(f"\n🚨 400 Bad Request - Common causes:")
                print("   - Invalid authorization code")
                print("   - Code already used (one-time use)")
                print("   - Mismatched redirect URI")
                print("   - Invalid client credentials")
            
            elif response.status_code == 401:
                print(f"\n🚨 401 Unauthorized - Common causes:")
                print("   - Invalid client_id or client_secret")
                print("   - App not properly configured")
            
            elif response.status_code == 403:
                print(f"\n🚨 403 Forbidden - Common causes:")
                print("   - Insufficient permissions")
                print("   - Conditional access policies")
            
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            print(f"Raw response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print(f"\n💡 Next Steps:")
    print("=" * 50)
    print("1. If you got a refresh token, the issue was in the original script")
    print("2. If you didn't get a refresh token, check the error details above")
    print("3. Common issues:")
    print("   - Authorization code already used (try getting a new one)")
    print("   - Azure app configuration issues")
    print("   - Network/proxy issues")

if __name__ == "__main__":
    debug_token_exchange()
