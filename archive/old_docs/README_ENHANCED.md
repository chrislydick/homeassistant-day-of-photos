# Enhanced iCloud Photos for Home Assistant

This enhanced version provides a robust, production-ready solution for fetching "on this day" photos from iCloud and integrating them with Home Assistant via Apache Airflow.

## 🚀 Key Improvements

- **Improved 2FA Handling**: More reliable two-factor authentication with better error handling
- **Session Persistence**: Saves authentication sessions to avoid repeated 2FA prompts
- **Better Logging**: Comprehensive logging for debugging and monitoring
- **Airflow Integration**: Designed specifically for daily Airflow execution at 4:00 AM
- **Error Recovery**: Graceful handling of network issues and API failures
- **File Organization**: Photos are organized by date for better management

## 📋 Prerequisites

1. **Apple ID Setup**:
   - Enable two-factor authentication on your Apple account
   - Create an app-specific password at [appleid.apple.com](https://appleid.apple.com/)
   - Note down your Apple ID email and app-specific password

2. **Python Environment**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apache Airflow** (for production use):
   - Airflow should be installed and running
   - Access to Airflow web UI and CLI

## 🛠️ Quick Setup

### 1. Test Your Setup

Run the setup script to test your iCloud connection:

```bash
python setup_airflow.py
```

This will:
- Test your iCloud credentials
- Download a few test photos
- Optionally set up Airflow variables

### 2. Manual Testing

You can also test the photo fetcher directly:

```bash
python icloud_photo_fetcher.py \
  --username "your_apple_id@example.com" \
  --password "your_app_specific_password" \
  --years-back 3 \
  --output-dir "./test_images"
```

### 3. Deploy to Airflow

1. **Copy the DAG file**:
   ```bash
   cp icloud_photos_dag.py /path/to/airflow/dags/
   cp icloud_photo_fetcher.py /path/to/airflow/dags/
   ```

2. **Set Airflow Variables** (if not done via setup script):
   ```bash
   airflow variables set ICLOUD_USERNAME "your_apple_id@example.com"
   airflow variables set ICLOUD_PASSWORD "your_app_specific_password"
   ```

3. **Restart Airflow**:
   ```bash
   airflow webserver restart
   airflow scheduler restart
   ```

## ⚙️ Configuration

### DAG Configuration

The DAG is configured to run daily at 4:00 AM. You can modify these settings in `icloud_photos_dag.py`:

```python
# Schedule (cron format)
SCHEDULE_INTERVAL = "0 4 * * *"  # 4:00 AM daily

# Number of years to look back
YEARS_BACK = 5

# Output directory for photos
OUTPUT_DIR = "/srv/homeassistant/media/day_photos"

# Session file location
SESSION_FILE = "/tmp/icloud_session.pickle"
```

### Environment Variables

For 2FA authentication, you can set these environment variables:

```bash
export ICLOUD_2FA_CODE="123456"  # Your 2FA verification code
export ICLOUD_2FA_DEVICE="0"     # Device index (0 for first device)
```

## 🔧 Troubleshooting

### 2FA Issues

If you encounter 2FA problems:

1. **First run**: Set the `ICLOUD_2FA_CODE` environment variable with your verification code
2. **Multiple devices**: Set `ICLOUD_2FA_DEVICE` to choose which device to use
3. **Manual code**: Generate a code manually on your iPhone/Mac and use it

### Session Issues

If authentication fails:

1. Delete the session file: `rm /tmp/icloud_session.pickle`
2. Re-run the task with 2FA code
3. Check that your app-specific password is correct

### Airflow Issues

If the DAG doesn't run:

1. Check Airflow logs: `airflow tasks logs icloud_day_photos fetch_icloud_photos`
2. Verify variables are set: `airflow variables list`
3. Test manually: `airflow dags test icloud_day_photos 2024-01-01`

## 📁 File Structure

```
homeassistant-day-of-photos/
├── icloud_photo_fetcher.py    # Enhanced photo fetcher
├── icloud_photos_dag.py       # Airflow DAG
├── setup_airflow.py           # Setup and testing script
├── requirements.txt           # Python dependencies
├── README_ENHANCED.md         # This file
└── test_images/               # Test output directory
```

## 🔄 Daily Operation

Once deployed, the system will:

1. **4:00 AM daily**: Airflow triggers the DAG
2. **Authentication**: Uses saved session or prompts for 2FA
3. **Photo search**: Finds photos from the same day across N years
4. **Download**: Saves photos to the configured directory
5. **Organization**: Files are named with date prefixes
6. **Home Assistant**: Photos are available for display

## 🎯 Home Assistant Integration

Configure Home Assistant to use the photos:

```yaml
# configuration.yaml
homeassistant:
  allowlist_external_dirs:
    - /srv/homeassistant/media/day_photos

# For WallPanel or similar
media_source:
```

## 📊 Monitoring

Monitor the DAG execution:

- **Airflow UI**: Check DAG runs and task logs
- **File system**: Monitor the output directory for new photos
- **Logs**: Check Airflow task logs for detailed information

## 🔒 Security Notes

- App-specific passwords are more secure than your main Apple ID password
- Session files contain sensitive authentication data
- Store credentials securely (Airflow variables are encrypted)
- Regularly rotate app-specific passwords

## 🆘 Support

If you encounter issues:

1. Check the logs for specific error messages
2. Test with the setup script first
3. Verify your Apple ID and app-specific password
4. Ensure 2FA is properly configured
5. Check network connectivity to iCloud services

## 🔄 Migration from Old Version

If you're migrating from the old `icloud_dag.py`:

1. The new version is backward compatible
2. Update your DAG file to use `icloud_photos_dag.py`
3. Copy the new `icloud_photo_fetcher.py` to your dags folder
4. Test with the setup script before deploying
5. The new version handles 2FA more reliably

---

**Note**: This enhanced version separates the photo fetching logic from the filtering logic, making it easier to maintain and extend. The photo filtering will be addressed in the next component. 