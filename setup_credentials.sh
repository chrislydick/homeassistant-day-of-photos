#!/bin/bash

# Setup script for OneDrive credentials
# This script helps you create the .env file with your OneDrive API credentials

echo "🔧 OneDrive Credentials Setup"
echo "============================="
echo ""
echo "This script will help you set up your OneDrive API credentials."
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Do you want to overwrite it? (y/N)"
    read -p "Overwrite? " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled."
        exit 1
    fi
fi

echo ""
echo "📋 You need to get your OneDrive API credentials from Microsoft Azure Portal:"
echo "   1. Go to https://portal.azure.com"
echo "   2. Sign in with your Microsoft account"
echo "   3. Go to 'App registrations' → 'New registration'"
echo "   4. Name: 'OneDrive Photos Fetcher'"
echo "   5. Supported account types: 'Accounts in any organizational directory and personal Microsoft accounts'"
echo "   6. Redirect URI: 'http://localhost:8080' (Web)"
echo "   7. Click 'Register'"
echo ""
echo "   8. Copy the 'Application (client) ID'"
echo "   9. Go to 'Certificates & secrets' → 'New client secret'"
echo "   10. Copy the 'Value' (this is your client secret)"
echo ""
echo "   11. Go to 'API permissions' → 'Add a permission'"
echo "   12. Choose 'Microsoft Graph' → 'Delegated permissions'"
echo "   13. Search for and add: 'Files.Read.All'"
echo "   14. Click 'Grant admin consent'"
echo ""

echo "🔑 Enter your OneDrive API credentials:"
echo ""

read -p "OneDrive Client ID: " client_id
read -p "OneDrive Client Secret: " client_secret

if [ -z "$client_id" ] || [ -z "$client_secret" ]; then
    echo "❌ Client ID and Client Secret are required."
    exit 1
fi

echo ""
echo "🏠 Home Assistant Configuration:"
echo ""

read -p "Home Assistant Server Host/IP: " ha_host
read -p "Home Assistant Username: " ha_user
read -p "Home Assistant Photos Directory: " ha_photos_dir
read -p "Home Assistant SSH Port (default: 22): " ha_ssh_port

# Set default SSH port if not provided
if [ -z "$ha_ssh_port" ]; then
    ha_ssh_port="22"
fi

echo ""
echo "📝 Creating .env file..."

# Create .env file
cat > .env << EOF
# OneDrive API Configuration
ONEDRIVE_CLIENT_ID=$client_id
ONEDRIVE_CLIENT_SECRET=$client_secret

# Home Assistant Server Configuration
HOMEASSISTANT_HOST=$ha_host
HOMEASSISTANT_USER=$ha_user
HOMEASSISTANT_PHOTOS_DIR=$ha_photos_dir
HOMEASSISTANT_SSH_PORT=$ha_ssh_port

# Optional: Override default years to look back (default is 10)
# ONEDRIVE_YEARS_BACK=15
EOF

echo "✅ .env file created successfully!"
echo ""
echo "🧪 To test your setup, run:"
echo "   python3 debug_onedrive_photos.py"
echo ""
echo "🚀 To run the main script:"
echo "   python3 onedrive_photos_script.py"
echo ""
echo "📄 Your .env file contains:"
echo "=========================="
cat .env
echo "=========================="
echo ""
echo "🔒 Keep your .env file secure and never commit it to version control!"
