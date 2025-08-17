#!/usr/bin/env python3
"""
Check Azure app configuration and provide specific guidance
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_azure_config():
    """Check Azure app configuration and provide guidance."""
    print("🔍 Azure App Configuration Check")
    print("=" * 60)
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    client_secret = os.getenv("ONEDRIVE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing ONEDRIVE_CLIENT_ID or ONEDRIVE_CLIENT_SECRET")
        return
    
    print(f"✅ Environment variables found")
    print(f"   Client ID: {client_id}")
    print(f"   Client Secret: {client_secret[:10]}...")
    
    print("\n🔧 Azure Portal Configuration Steps:")
    print("=" * 60)
    
    print("1. Go to Azure Portal → App registrations → Your app")
    print("2. Click 'Authentication' in the left menu")
    print("3. Check these settings:")
    print()
    
    print("📋 Platform Configuration:")
    print("   - You MUST have a 'Web' platform configured")
    print("   - 'Mobile and desktop applications' alone won't work for refresh tokens")
    print("   - If you only see 'Mobile and desktop applications', add a 'Web' platform")
    print()
    
    print("📋 Redirect URIs:")
    print("   - Should include exactly: http://localhost:8080")
    print("   - No extra spaces, no trailing slashes")
    print("   - Case sensitive")
    print()
    
    print("📋 Implicit grant and hybrid flows:")
    print("   - ALL of these should be UNCHECKED:")
    print("     [ ] Access tokens")
    print("     [ ] ID tokens")
    print("   - If any are checked, refresh tokens won't work")
    print()
    
    print("📋 API Permissions:")
    print("   - Go to 'API permissions' tab")
    print("   - Should have: Microsoft Graph → Files.Read.All")
    print("   - Status should be 'Granted for [your organization]'")
    print()
    
    print("🚨 Common Issues:")
    print("=" * 60)
    print("1. App configured for implicit flow (refresh tokens don't work)")
    print("2. Missing 'Web' platform configuration")
    print("3. Incorrect redirect URI")
    print("4. Implicit grant flows enabled")
    print()
    
    print("🔧 Quick Fix Steps:")
    print("=" * 60)
    print("1. Add 'Web' platform if missing:")
    print("   - Click 'Add a platform'")
    print("   - Select 'Web'")
    print("   - Add redirect URI: http://localhost:8080")
    print()
    print("2. Disable implicit flows:")
    print("   - Uncheck 'Access tokens'")
    print("   - Uncheck 'ID tokens'")
    print()
    print("3. Save changes")
    print("4. Test OAuth flow again")
    print()
    
    print("🧪 Test Command:")
    print("=" * 60)
    print("After fixing Azure settings, run:")
    print("python3 test_oauth_flow.py")
    print()
    print("You should see:")
    print("✅ Refresh token: [some number] characters")
    print("✅ Refresh token works correctly")

def test_current_config():
    """Test the current configuration to see what's happening."""
    print("\n🧪 Testing Current Configuration")
    print("=" * 60)
    
    client_id = os.getenv("ONEDRIVE_CLIENT_ID")
    
    # Test authorization URL
    auth_url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        f"client_id={client_id}&"
        "response_type=code&"
        "redirect_uri=http://localhost:8080&"
        "scope=Files.Read.All offline_access&"
        "response_mode=query"
    )
    
    print("Current authorization URL:")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    
    print("\n📋 Check this URL in your browser:")
    print("1. Does it redirect to Microsoft login?")
    print("2. After login, does it redirect to localhost:8080?")
    print("3. Does the redirect URL contain a 'code' parameter?")
    print()
    print("If any of these fail, there's an Azure configuration issue.")

def main():
    """Main function."""
    check_azure_config()
    test_current_config()
    
    print("\n💡 Next Steps:")
    print("=" * 60)
    print("1. Fix Azure app configuration as described above")
    print("2. Run: python3 test_oauth_flow.py")
    print("3. If still no refresh token, check Azure app logs")
    print("4. Consider creating a new app registration if issues persist")

if __name__ == "__main__":
    main()
