#!/usr/bin/env python3
"""
Test alternative scope combinations for refresh tokens
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_scope_combinations():
    """Test different scope combinations to see which ones return refresh tokens."""
    print("🔍 Testing Alternative Scope Combinations")
    print("=" * 60)
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing ONEDRIVE_CLIENT_ID or ONEDRIVE_CLIENT_SECRET")
        return
    
    # Different scope combinations to test
    scope_combinations = [
        "Files.Read.All offline_access",
        "Files.Read.All offline_access profile",
        "Files.Read.All offline_access openid",
        "Files.Read.All offline_access profile openid",
        "Files.Read.All",
        "offline_access Files.Read.All"
    ]
    
    for i, scope in enumerate(scope_combinations, 1):
        print(f"\n🧪 Test {i}: Scope = '{scope}'")
        print("=" * 50)
        
        # Get authorization URL
        auth_url = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
            f"client_id={client_id}&"
            "response_type=code&"
            "redirect_uri=http://localhost:8080&"
            f"scope={scope}&"
            "response_mode=query"
        )
        
        print(f"Authorization URL:")
        print(auth_url)
        print()
        print("Please visit this URL in your browser and get the authorization code.")
        print("(You can skip this test by pressing Enter without a code)")
        
        auth_code = input("Enter the authorization code (or press Enter to skip): ").strip()
        
        if not auth_code:
            print("⏭️ Skipping this test")
            continue
        
        # Exchange for tokens
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
                
                print(f"✅ Success! Status: {response.status_code}")
                print(f"   Access token: {'✅' if 'access_token' in token_data else '❌'}")
                print(f"   Refresh token: {'✅' if 'refresh_token' in token_data and token_data['refresh_token'] else '❌'}")
                print(f"   Scope returned: {token_data.get('scope', 'N/A')}")
                
                if 'refresh_token' in token_data and token_data['refresh_token']:
                    print(f"   🎉 REFRESH TOKEN FOUND! Length: {len(token_data['refresh_token'])} characters")
                    print(f"   This scope combination works: '{scope}'")
                    return scope
                else:
                    print(f"   ❌ No refresh token with scope: '{scope}'")
            else:
                print(f"❌ Failed! Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n💡 Results Summary:")
    print("=" * 60)
    print("None of the scope combinations returned a refresh token.")
    print("This suggests the issue is with Azure app configuration, not scopes.")
    print()
    print("Additional things to check:")
    print("1. API permissions status (should be 'Granted for organization')")
    print("2. Supported account types in app registration")
    print("3. Token lifetime policies")
    print("4. Conditional access policies")

if __name__ == "__main__":
    test_scope_combinations()
