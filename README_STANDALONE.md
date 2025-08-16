# OneDrive Photos Script - Standalone Version

This is a standalone Python script that fetches photos from OneDrive for a specific date across multiple years and transfers them to a Home Assistant server. It's designed to be run via crontab instead of using Apache Airflow.

## Features

- 🔐 **OAuth2 Authentication**: Secure authentication with OneDrive API
- 📅 **Date-based Search**: Find photos from the same day across multiple years
- 🖼️ **Multiple Formats**: Supports JPG, PNG, GIF, HEIC, RAW, and more
- 📤 **Home Assistant Transfer**: Automatically transfers photos to Home Assistant server via SCP
- 📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- ⚡ **Crontab Ready**: Designed to run automatically via cron jobs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_standalone.txt
```

### 2. Set Up Environment Variables

Copy the template and fill in your credentials:

```bash
cp env_template.txt .env
```

Edit `.env` with your actual values:

```bash
# OneDrive API Configuration
ONEDRIVE_CLIENT_ID=your_actual_client_id
ONEDRIVE_CLIENT_SECRET=your_actual_client_secret

# Home Assistant Server Configuration
HOMEASSISTANT_HOST=192.168.1.100
HOMEASSISTANT_USER=homeassistant
HOMEASSISTANT_PHOTOS_DIR=/config/www/photos
HOMEASSISTANT_SSH_PORT=22
```

### 3. Set Up OneDrive App

1. Go to [Microsoft Azure Portal](https://portal.azure.com)
2. Create a new app registration
3. Set redirect URI to `http://localhost:8080`
4. Add `Files.Read.All` permission
5. Copy the Client ID and Client Secret to your `.env` file

### 4. First Run (Authentication)

Run the script manually for the first time to authenticate:

```bash
python3 onedrive_photos_script.py
```

This will open a browser for OAuth authentication. The token will be saved for future runs.

### 5. Set Up Crontab

Use the provided setup script:

```bash
./setup_crontab.sh
```

Or manually add to crontab:

```bash
# Run daily at 4:00 AM
0 4 * * * cd /path/to/script && python3 onedrive_photos_script.py >> cron.log 2>&1
```

## Usage

### Basic Usage

```bash
# Run for today's date
python3 onedrive_photos_script.py

# Run for a specific date
python3 onedrive_photos_script.py --date 2024-12-25

# Look back 10 years instead of 5
python3 onedrive_photos_script.py --years-back 10
```

### Advanced Options

```bash
python3 onedrive_photos_script.py \
  --date 2024-12-25 \
  --years-back 10 \
  --output-dir /tmp/my_photos \
  --photos-folder "Camera Roll" \
  --skip-transfer
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--date` | Target date (YYYY-MM-DD) | Today |
| `--years-back` | Number of years to look back | 5 |
| `--output-dir` | Local temporary directory | `/tmp/onedrive_photos_temp` |
| `--client-id` | OneDrive app client ID | From env var |
| `--client-secret` | OneDrive app client secret | From env var |
| `--token-file` | Path to token file | `./onedrive_token.pickle` |
| `--photos-folder` | OneDrive photos folder name | `Pictures` |
| `--homeassistant-host` | Home Assistant server host | From env var |
| `--homeassistant-user` | Home Assistant server user | From env var |
| `--homeassistant-photos-dir` | Home Assistant photos directory | From env var |
| `--homeassistant-ssh-port` | Home Assistant SSH port | `22` |
| `--skip-transfer` | Skip transferring to Home Assistant | False |

## Environment Variables

The script reads configuration from environment variables (can be set in `.env` file):

| Variable | Description | Required |
|----------|-------------|----------|
| `ONEDRIVE_CLIENT_ID` | OneDrive app client ID | Yes |
| `ONEDRIVE_CLIENT_SECRET` | OneDrive app client secret | Yes |
| `HOMEASSISTANT_HOST` | Home Assistant server IP/hostname | Yes* |
| `HOMEASSISTANT_USER` | Home Assistant server username | Yes* |
| `HOMEASSISTANT_PHOTOS_DIR` | Home Assistant photos directory | Yes* |
| `HOMEASSISTANT_SSH_PORT` | Home Assistant SSH port | No (default: 22) |

*Required unless using `--skip-transfer`

## File Structure

```
homeassistant-day-of-photos/
├── onedrive_photos_script.py      # Main script
├── setup_crontab.sh               # Crontab setup helper
├── requirements_standalone.txt    # Python dependencies
├── env_template.txt               # Environment template
├── .env                          # Your environment variables (create this)
├── onedrive_token.pickle         # OAuth token (created automatically)
├── onedrive_photos.log           # Script logs
├── cron.log                      # Crontab execution logs
└── archive/
    └── airflow_code/             # Old Airflow files
        ├── onedrive_photos_dag.py
        └── onedrive_photos_fetcher.py
```

## Logging

The script creates two log files:

- **`onedrive_photos.log`**: Detailed script execution logs
- **`cron.log`**: Crontab execution output

View logs in real-time:

```bash
# Script logs
tail -f onedrive_photos.log

# Crontab logs
tail -f cron.log
```

## Troubleshooting

### Authentication Issues

1. **Token expired**: Delete `onedrive_token.pickle` and re-authenticate
2. **Invalid credentials**: Check your `.env` file
3. **Permission denied**: Ensure your OneDrive app has `Files.Read.All` permission

### Transfer Issues

1. **SSH connection failed**: Check Home Assistant server connectivity
2. **Permission denied**: Ensure SSH key authentication is set up
3. **Directory not found**: Check `HOMEASSISTANT_PHOTOS_DIR` path

### Common Commands

```bash
# Test SSH connection
ssh user@homeassistant-host

# Check script permissions
ls -la onedrive_photos_script.py

# View current crontab
crontab -l

# Remove crontab entry
crontab -e

# Test script manually
python3 onedrive_photos_script.py --skip-transfer
```

## Migration from Airflow

If you're migrating from the Airflow version:

1. **Move old files**: Airflow files are now in `archive/airflow_code/`
2. **Update environment**: Use `.env` instead of Airflow variables
3. **Set up crontab**: Use `./setup_crontab.sh` instead of Airflow scheduling
4. **Test manually**: Run the script manually before setting up cron

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The OAuth token is stored locally in `onedrive_token.pickle`
- SSH keys should be used for Home Assistant server access
- Consider running the script as a dedicated user with limited permissions

## Support

For issues or questions:

1. Check the logs: `tail -f onedrive_photos.log`
2. Test manually: `python3 onedrive_photos_script.py --skip-transfer`
3. Verify environment variables are set correctly
4. Ensure OneDrive app permissions are configured properly
