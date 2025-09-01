#!/bin/bash
# Enhanced Crontab Setup Script with AI Image Analysis
# This script sets up a crontab job that downloads photos and uses AI to filter quality

set -e

echo "🚀 Setting up Enhanced Crontab with AI Image Analysis"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "onedrive_photos_script_enhanced.py" ]; then
    echo "❌ Error: Please run this script from the homeassistant-day-of-photos directory"
    exit 1
fi

# Check if AI dependencies are available
echo "🔍 Checking AI dependencies..."
if python3 -c "import torch, torchvision, cv2" 2>/dev/null; then
    echo "✅ AI dependencies are available"
    AI_AVAILABLE=true
else
    echo "⚠️  AI dependencies not available. Install with: pip3 install -r requirements_standalone.txt"
    echo "   The script will still work without AI analysis"
    AI_AVAILABLE=false
fi

# Get current user
CURRENT_USER=$(whoami)
SCRIPT_DIR=$(pwd)
SCRIPT_PATH="$SCRIPT_DIR/onedrive_photos_script_enhanced.py"
LOG_FILE="$SCRIPT_DIR/cron.log"

echo ""
echo "📋 Current Configuration:"
echo "   User: $CURRENT_USER"
echo "   Script: $SCRIPT_PATH"
echo "   Log File: $LOG_FILE"
echo "   AI Available: $AI_AVAILABLE"

echo ""
echo "🔄 Setting up crontab job..."

# Create the crontab entry
if [ "$AI_AVAILABLE" = true ]; then
    # With AI analysis enabled
    CRON_ENTRY="00 03 * * * cd $SCRIPT_DIR && python3 $SCRIPT_PATH --ai-device auto --ai-confidence 0.7 --filter-by-ai --move-bad-images >> $LOG_FILE 2>&1"
    echo "   ✅ AI analysis will be enabled"
    echo "   ✅ Only good images will be transferred"
    echo "   ✅ Bad images will be moved to bad_images folder"
else
    # Without AI analysis
    CRON_ENTRY="00 03 * * * cd $SCRIPT_DIR && python3 $SCRIPT_PATH >> $LOG_FILE 2>&1"
    echo "   ⚠️  AI analysis will be skipped"
fi

echo ""
echo "📝 Crontab entry to be added:"
echo "   $CRON_ENTRY"

echo ""
echo "❓ Do you want to proceed with this setup? (y/N)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo "🔧 Setting up crontab..."
    
    # Check if crontab already exists
    if crontab -l 2>/dev/null | grep -q "onedrive_photos_script_enhanced.py"; then
        echo "⚠️  Found existing crontab entry. Removing old entry..."
        crontab -l 2>/dev/null | grep -v "onedrive_photos_script_enhanced.py" | crontab -
    fi
    
    # Add new crontab entry
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    
    echo "✅ Crontab job added successfully!"
    echo ""
    echo "📋 Current crontab entries:"
    crontab -l
    
    echo ""
    echo "🎯 The script will now run daily at 3:00 AM and:"
    echo "   1. Download photos from OneDrive for the current date"
    echo "   2. Analyze image quality using AI (if available)"
    echo "   3. Transfer only good images to Home Assistant"
    echo "   4. Log all activities to $LOG_FILE"
    
    if [ "$AI_AVAILABLE" = true ]; then
        echo ""
        echo "🤖 AI Analysis Features:"
        echo "   - Automatic image quality assessment"
        echo "   - Filtering out screenshots, documents, blurry images"
        echo "   - Keeping only people, pets, scenery, and good photos"
        echo "   - Bad images moved to bad_images folder for review"
    fi
    
else
    echo "❌ Setup cancelled"
    exit 1
fi

echo ""
echo "🔍 To test the setup manually, run:"
echo "   python3 $SCRIPT_PATH --skip-transfer"
echo ""
echo "🧪 To test AI analysis, run:"
echo "   python3 test_ai_analyzer.py"
echo ""
echo "📖 For more options, run:"
echo "   python3 $SCRIPT_PATH --help"
echo ""
echo "🎉 Setup complete!"
