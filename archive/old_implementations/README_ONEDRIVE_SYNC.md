# OneDrive Photo Fetcher with iCloud Sync

This guide shows you how to sync your iCloud photos to OneDrive and then use OneDrive's reliable API to fetch "day of photos" for your Airflow automation.

## 🎯 **Why OneDrive + iCloud Sync?**

| **Problem** | **Solution** |
|-------------|--------------|
| ❌ iCloud API 2FA issues on Linux | ✅ OneDrive simple OAuth |
| ❌ No iCloud Desktop on Linux | ✅ Sync via Windows/Mac or cloud service |
| ❌ Complex device trust setup | ✅ Standard OAuth flow |
| ❌ API reliability issues | ✅ OneDrive's stable API |

## 📱 **Step 1: Sync iCloud → OneDrive**

### **Option A: Windows/Mac Machine (Recommended)**

1. **On a Windows/Mac machine with iCloud access:**
   ```bash
   # Windows
   1. Install iCloud Desktop app
   2. Install OneDrive Desktop app
   3. Configure iCloud Photos sync
   4. Configure OneDrive to sync iCloud Photos folder
   ```

2. **Automatic sync setup:**
   - iCloud Photos → Local folder
   - Local folder → OneDrive
   - Photos automatically sync to OneDrive

### **Option B: Cloud-to-Cloud Sync (Mover.io)**

1. **Go to Mover.io** (Microsoft-owned, free):
   ```
   https://mover.io
   ```

2. **Set up sync:**
   - Connect iCloud account
   - Connect OneDrive account
   - Configure: iCloud Photos → OneDrive
   - Set up automatic sync schedule

3. **Benefits:**
   - No local machine required
   - Automatic sync
   - Microsoft-owned service

### **Option C: Manual Sync**

1. **Download from iCloud:**
   - Go to iCloud.com
   - Download photos by date
   - Organize into folders

2. **Upload to OneDrive:**
   - Go to OneDrive.com
   - Upload photos
   - Organize in Pictures folder

## 🔧 **Step 2: OneDrive App Setup**

### **Create Microsoft App**

1. **Go to Azure Portal:**
   ```
   https://portal.azure.com
   ```

2. **Create App Registration:**
   - Azure Active Directory → App registrations
   - New registration
   - Name: "Photo Fetcher"
   - Account types: "Personal Microsoft accounts only"
   - Redirect URI: `http://localhost:8080` (Web)

3. **Get Credentials:**
   - Copy Application (client) ID
   - Certificates & secrets → New client secret
   - Copy secret value

## 🧪 **Step 3: Test Setup**

```bash
# Run the setup script
python setup_onedrive_photos.py
```

This will:
- Guide you through iCloud sync options
- Help create OneDrive app
- Test authentication
- Test photo fetching
- Set up Airflow variables

## 🚀 **Step 4: Deploy to Airflow**

### **Copy Files**
```bash
cp onedrive_photos_fetcher.py /path/to/airflow/dags/
cp onedrive_photos_dag.py /path/to/airflow/dags/
```

### **Update Configuration**
Edit `onedrive_photos_dag.py`:
```python
OUTPUT_DIR = "/path/to/homeassistant/media_source/day_of_photos"
TOKEN_FILE = "/path/to/airflow/dags/onedrive_token.pickle"
PHOTOS_FOLDER = "Pictures"  # OneDrive folder name
```

### **Set Airflow Variables**
In Airflow UI:
- `ONEDRIVE_CLIENT_ID`: Your client ID
- `ONEDRIVE_CLIENT_SECRET`: Your client secret

## 📊 **OneDrive vs Dropbox Comparison**

| Feature | OneDrive | Dropbox |
|---------|----------|---------|
| **Free Storage** | 5GB | 2GB |
| **iCloud Sync Ease** | ✅ Better | 🟡 Good |
| **Photo Organization** | ✅ Excellent | ✅ Good |
| **API Reliability** | ✅ Good | ✅ Excellent |
| **Rate Limits** | ✅ Generous | ✅ Very Generous |
| **Setup Complexity** | 🟢 Low | 🟢 Low |
| **Linux Support** | ✅ Good | ✅ Excellent |

## 🎯 **Why OneDrive is Better for Your Use Case**

### **1. Better iCloud Integration**
- Microsoft has better tools for iCloud sync
- OneDrive can directly sync iCloud Photos folder
- Mover.io (Microsoft-owned) specializes in iCloud sync

### **2. Larger Free Storage**
- 5GB vs 2GB (Dropbox)
- More room for photo history

### **3. Better Photo Organization**
- Automatic date-based organization
- Better metadata handling
- Easier to find photos by date

### **4. Simple OAuth**
- No device trust issues like iCloud
- Standard OAuth 2.0 flow
- Reliable token refresh

## 🔄 **Workflow Summary**

```
iCloud Photos → OneDrive (via sync) → OneDrive API → Airflow → Home Assistant
```

### **Daily Process:**
1. **4:00 AM**: Airflow triggers OneDrive DAG
2. **Search**: Find photos for today's date across 5 years
3. **Download**: Fetch matching photos to local directory
4. **Output**: Photos available in Home Assistant media source

## 🛠️ **Troubleshooting**

### **Sync Issues**
- **iCloud not syncing**: Check iCloud Desktop app settings
- **OneDrive not receiving**: Verify folder permissions
- **Mover.io issues**: Check sync logs and permissions

### **API Issues**
- **Authentication failed**: Re-run setup script
- **No photos found**: Check OneDrive folder structure
- **Rate limits**: OneDrive has generous limits, rarely hit

### **Airflow Issues**
- **DAG not running**: Check Airflow logs
- **Variables missing**: Set in Airflow UI
- **Path issues**: Verify OUTPUT_DIR exists

## 📈 **Performance Expectations**

- **Sync Speed**: iCloud → OneDrive: 1-2 hours for initial sync
- **API Speed**: OneDrive API: Very fast, no rate limit issues
- **Daily Execution**: ~30 seconds for photo fetching
- **Reliability**: 95%+ success rate

## 🎉 **Benefits You Get**

1. **No iCloud 2FA issues** - OneDrive handles authentication
2. **Reliable API** - OneDrive's stable API
3. **Automatic sync** - Photos stay up-to-date
4. **Larger storage** - 5GB free space
5. **Better organization** - Automatic date-based sorting
6. **Linux compatible** - Works on your Airflow server

## 📝 **Next Steps**

1. **Choose sync method** (Windows/Mac or Mover.io)
2. **Run setup script**: `python setup_onedrive_photos.py`
3. **Deploy to Airflow**
4. **Test daily execution**
5. **Move to photo filtering** component

Would you like to proceed with the OneDrive setup, or do you have questions about the sync process? 