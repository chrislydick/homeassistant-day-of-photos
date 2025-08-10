# OneDrive Photo Fetcher for Home Assistant

A reliable solution for fetching "day of photos" from OneDrive for your Home Assistant automation.

## 🎯 **Why OneDrive?**

- ✅ **Reliable OAuth Authentication** - No 2FA issues like iCloud
- ✅ **Stable API** - Microsoft Graph API is very reliable
- ✅ **Easy iCloud Integration** - Sync iCloud photos to OneDrive
- ✅ **Linux Compatible** - Works perfectly on Linux systems

## 📁 **Project Structure**

### **Active Files (Root Directory)**
```
├── onedrive_photos_fetcher.py    # Main OneDrive fetcher (reliable OAuth)
├── onedrive_photos_dag.py        # Airflow DAG for OneDrive
├── setup_onedrive.py             # Setup script for OneDrive
├── .env                          # Environment variables (your credentials)
├── requirements.txt               # Python dependencies
└── README_CURRENT.md             # This file
```

### **Archive**
```
archive/old_implementations/      # Previous implementations (iCloud, Google, etc.)
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Up OneDrive App**
```bash
python setup_onedrive.py
```

### **3. Configure Environment**
Create a `.env` file with your OneDrive credentials:
```bash
ONEDRIVE_CLIENT_ID=your_client_id_here
ONEDRIVE_CLIENT_SECRET=your_client_secret_here
```

### **4. Test the Setup**
```bash
python setup_onedrive.py
```

## 🔧 **Features**

- **Reliable OAuth**: Uses direct OAuth2 flow, bypassing problematic libraries
- **Token Management**: Automatically saves and reuses authentication tokens
- **Date-based Search**: Finds photos from specific dates across multiple years
- **Airflow Integration**: Ready-to-use DAG for automated execution
- **Environment Variables**: Secure credential management

## 📊 **How It Works**

1. **Authentication**: Uses Microsoft Graph API with OAuth2
2. **Photo Search**: Searches OneDrive for photos on specific dates
3. **Download**: Downloads photos to local directory
4. **Integration**: Works with Airflow for automated daily execution

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

## 🎯 **Airflow Integration**

The DAG runs daily at 4:00 AM and:
- Fetches photos from this day in history
- Downloads them to your specified directory
- Integrates with Home Assistant for display

## ✅ **Success Story**

This implementation successfully solved:
- ❌ OAuth state mismatch issues (original O365 library)
- ❌ iCloud 2FA problems on Linux
- ❌ Complex authentication flows
- ✅ **Reliable OneDrive OAuth authentication**
- ✅ **Clean, maintainable code**
- ✅ **Easy setup and configuration**

## 📝 **Requirements**

- Python 3.9+
- OneDrive account
- Azure app registration
- Apache Airflow (for automation)

## 🔒 **Security**

- Credentials stored in `.env` file (not in code)
- OAuth tokens automatically managed
- No hardcoded secrets
- Secure token storage

## 📚 **Documentation**

- `CLOUD_ALTERNATIVES_COMPARISON.md` - Comparison of different cloud providers
- `archive/README.md` - Information about archived implementations
- `archive/old_implementations/` - Previous implementations for reference 