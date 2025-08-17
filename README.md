# OneDrive Photo Fetcher for Home Assistant

A reliable solution for fetching "day of photos" from OneDrive for your Home Assistant automation. **Now available as a standalone script that runs via crontab!**

## 🎯 **Why OneDrive?**

- ✅ **Reliable OAuth Authentication** - No 2FA issues like iCloud
- ✅ **Stable API** - Microsoft Graph API is very reliable
- ✅ **Easy iCloud Integration** - Sync iCloud photos to OneDrive
- ✅ **Linux Compatible** - Works perfectly on Linux systems
- ✅ **Standalone Script** - No Airflow required, runs via crontab

## 🚀 **Quick Start (Standalone Version)**

The project now includes a standalone script that doesn't require Apache Airflow. This is the recommended approach.

### **1. Install Dependencies**
```bash
pip install -r requirements_standalone.txt
```

### **2. Set Up Environment**
```bash
cp env_template.txt .env
# Edit .env with your OneDrive and Home Assistant credentials
```

### **3. First Run (Authentication)**
```bash
python3 onedrive_photos_script.py
```

### **4. Set Up Crontab**
```bash
./setup_crontab.sh
```

**📖 For detailed instructions, see [README_STANDALONE.md](README_STANDALONE.md)**

## 📁 **Project Structure**

### **Active Files (Standalone Version)**
```
├── onedrive_photos_script.py      # Main standalone script
├── onedrive_photos_script_enhanced.py  # Enhanced version with better token management
├── setup_crontab.sh               # Crontab setup helper
├── requirements_standalone.txt    # Python dependencies
├── env_template.txt               # Environment template
├── README_STANDALONE.md           # Detailed standalone documentation
├── debug/                         # Debug and diagnostic scripts
└── README.md                      # This file
```

### **Archived Files**
```
└── archive/
    └── airflow_code/              # Old Airflow implementation
        ├── onedrive_photos_dag.py
        └── onedrive_photos_fetcher.py
```

## 🔧 **Features**

- **Reliable OAuth**: Uses direct OAuth2 flow, bypassing problematic libraries
- **Token Management**: Automatically saves and reuses authentication tokens
- **Date-based Search**: Finds photos from specific dates across multiple years
- **Crontab Ready**: Designed to run automatically via cron jobs
- **Home Assistant Integration**: Automatically transfers photos to Home Assistant server
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 🔄 **iCloud → OneDrive Sync**

Since you're on Linux, sync your iCloud photos to OneDrive:

### **Option A: Windows/Mac Machine**
1. Install iCloud Desktop app
2. Install OneDrive Desktop app
3. Configure OneDrive to sync iCloud Photos folder
4. Photos automatically sync to OneDrive

### **Option B: Cloud-to-Cloud Sync**
1. Use [Mover.io](https://mover.io) (Microsoft-owned, free)
2. Connect iCloud account
3. Connect OneDrive account
4. Set up automatic sync

## 📝 **Requirements**

- Python 3.9+
- OneDrive account
- Azure app registration
- SSH access to Home Assistant server

## 🔒 **Security**

- Credentials stored in `.env` file (not in code)
- OAuth tokens automatically managed
- No hardcoded secrets
- Secure token storage

## 📚 **Documentation**

- **[README_STANDALONE.md](README_STANDALONE.md)** - Complete standalone setup and usage guide
- `archive/README.md` - Information about archived implementations
- `archive/old_implementations/` - Previous implementations for reference

## 🔄 **Migration from Airflow**

If you were using the Airflow version:

1. **Old files moved**: Airflow files are now in `archive/airflow_code/`
2. **New approach**: Use the standalone script with crontab
3. **Environment**: Use `.env` instead of Airflow variables
4. **Scheduling**: Use `./setup_crontab.sh` instead of Airflow DAGs

## 🆘 **Need Help?**

1. Check the standalone documentation: [README_STANDALONE.md](README_STANDALONE.md)
2. View logs: `tail -f onedrive_photos.log`
3. Test manually: `python3 onedrive_photos_script.py --skip-transfer`
4. Check environment variables are set correctly
