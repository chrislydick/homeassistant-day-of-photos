#!/bin/bash

# Setup script for OneDrive Photos Crontab
# This script helps you set up a daily cron job to run the OneDrive photos script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/onedrive_photos_script_enhanced.py"

echo "🔧 OneDrive Photos Crontab Setup"
echo "=================================="
echo ""
echo "This script will help you set up a daily cron job to run the OneDrive photos script."
echo ""

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Check if script is executable
if [ ! -x "$SCRIPT_PATH" ]; then
    echo "⚠️  Making script executable..."
    chmod +x "$SCRIPT_PATH"
fi

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "⚠️  Warning: .env file not found. Please create one based on env_template.txt"
    echo "   Copy env_template.txt to .env and fill in your credentials:"
    echo "   cp env_template.txt .env"
    echo ""
fi

echo "📋 Current crontab entries:"
echo "============================"
crontab -l 2>/dev/null || echo "No crontab entries found"
echo ""

echo "🕐 What time would you like to run the script daily? (24-hour format)"
echo "   Example: 04:00 for 4:00 AM, 14:30 for 2:30 PM"
read -p "Enter time (HH:MM): " run_time

# Validate time format
if [[ ! $run_time =~ ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$ ]]; then
    echo "❌ Invalid time format. Please use HH:MM (24-hour format)"
    exit 1
fi

# Parse time
hour=$(echo $run_time | cut -d: -f1)
minute=$(echo $run_time | cut -d: -f2)

# Create cron entry
cron_entry="$minute $hour * * * cd $SCRIPT_DIR && python3 $SCRIPT_PATH >> $SCRIPT_DIR/cron.log 2>&1"

echo ""
echo "📝 New cron entry to be added:"
echo "==============================="
echo "$cron_entry"
echo ""

read -p "Add this cron entry? (y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    # Get current crontab
    current_crontab=$(crontab -l 2>/dev/null)
    
    # Add new entry
    if [ -z "$current_crontab" ]; then
        echo "$cron_entry" | crontab -
    else
        echo "$current_crontab"$'\n'"$cron_entry" | crontab -
    fi
    
    echo "✅ Cron job added successfully!"
    echo ""
    echo "📋 Updated crontab:"
    echo "==================="
    crontab -l
    echo ""
    echo "📝 The script will run daily at $run_time"
    echo "📄 Logs will be written to: $SCRIPT_DIR/cron.log"
    echo "📄 Script logs will be written to: $SCRIPT_DIR/onedrive_photos.log"
    echo ""
    echo "🔧 To remove the cron job later, run: crontab -e"
else
    echo "❌ Cron job not added."
fi

echo ""
echo "📚 Additional information:"
echo "=========================="
echo "• Script path: $SCRIPT_PATH"
echo "• Environment file: $SCRIPT_DIR/.env"
echo "• Cron logs: $SCRIPT_DIR/cron.log"
echo "• Script logs: $SCRIPT_DIR/onedrive_photos.log"
echo ""
echo "🧪 To test the script manually, run:"
echo "   cd $SCRIPT_DIR && python3 $SCRIPT_PATH"
echo ""
echo "🔍 To view logs:"
echo "   tail -f $SCRIPT_DIR/onedrive_photos.log"
echo "   tail -f $SCRIPT_DIR/cron.log"
