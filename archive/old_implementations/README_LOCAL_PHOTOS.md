# Local Photos Solution for Home Assistant

This solution provides a robust, production-ready way to fetch "on this day" photos from your **local photo library** and integrate them with Home Assistant via Apache Airflow. **This approach completely avoids all cloud sync and 2FA issues.**

## 🚀 Why Local Photos Instead of Cloud Solutions?

### **Cloud Problems Solved:**
- ❌ **No 2FA device trust issues** - Works directly with your local files
- ❌ **No cloud sync required** - Uses your existing photo organization
- ❌ **No API rate limits** - No network dependencies
- ❌ **No authentication complexity** - Direct file system access
- ❌ **No data privacy concerns** - Photos never leave your system

### **Local Photos Advantages:**
- ✅ **Works with any photo organization** - Flexible directory structure
- ✅ **Multiple date detection methods** - EXIF, filename patterns, file dates
- ✅ **Faster execution** - No network downloads required
- ✅ **No external dependencies** - Self-contained solution
- ✅ **Privacy-focused** - All processing happens locally

## 📋 Prerequisites

1. **Local Photo Library**:
   - Organized photo directory (any structure works)
   - Photos with dates (EXIF data, filename patterns, or file dates)

2. **Python Environment**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apache Airflow** (for production use):
   - Airflow should be installed and running
   - Access to Airflow web UI and CLI

## 🛠️ Quick Setup

### 1. Test Your Setup

Run the setup script to test your local photo directory:

```bash
python setup_local_photos.py
```

This will:
- Check your photo directory structure
- Test photo finding and copying
- Configure paths and date formats
- Optionally set up Airflow variables

### 2. Manual Testing

You can also test the photo fetcher directly:

```bash
python local_photos_fetcher.py \
  --source-dir "/path/to/your/photos" \
  --years-back 3 \
  --output-dir "./test_images"
```

### 3. Deploy to Airflow

1. **Copy the files to Airflow**:
   ```bash
   cp local_photos_dag.py /path/to/airflow/dags/
   cp local_photos_fetcher.py /path/to/airflow/dags/
   ```

2. **Update the source directory** in `local_photos_dag.py`:
   ```python
   SOURCE_DIR = "/path/to/your/photo/library"  # Your actual photo directory
   ```

3. **Set Airflow Variables** (if not done via setup script):
   ```bash
   airflow variables set LOCAL_PHOTOS_SOURCE_DIR "/path/to/your/photos"
   airflow variables set LOCAL_PHOTOS_OUTPUT_DIR "/srv/homeassistant/media/day_photos"
   airflow variables set LOCAL_PHOTOS_DATE_FORMAT "YYYY-MM-DD"
   ```

4. **Restart Airflow**:
   ```bash
   airflow webserver restart
   airflow scheduler restart
   ```

## ⚙️ Configuration

### DAG Configuration

The DAG is configured to run daily at 4:00 AM. You can modify these settings in `local_photos_dag.py`:

```python
# Schedule (cron format)
SCHEDULE_INTERVAL = "0 4 * * *"  # 4:00 AM daily

# Number of years to look back
YEARS_BACK = 5

# Source and output directories
SOURCE_DIR = "/path/to/your/photo/library"
OUTPUT_DIR = "/srv/homeassistant/media/day_photos"

# Date format in filenames
DATE_FORMAT = "YYYY-MM-DD"
```

### Supported Photo Formats

The solution supports all common photo formats:
- **JPEG**: `.jpg`, `.jpeg`
- **PNG**: `.png`
- **GIF**: `.gif`
- **TIFF**: `.tiff`
- **HEIC**: `.heic`, `.heif`
- **WebP**: `.webp`
- **RAW**: `.raw`, `.cr2`, `.nef`

### Date Detection Methods

The system uses multiple methods to find photo dates (in order of preference):

1. **EXIF Data**: Extracts `DateTimeOriginal` or `DateTime` from photo metadata
2. **Filename Patterns**: Recognizes common date formats in filenames:
   - `YYYY-MM-DD` (e.g., `2024-01-15_photo.jpg`)
   - `YYYY_MM_DD` (e.g., `2024_01_15_photo.jpg`)
   - `YYYYMMDD` (e.g., `20240115_photo.jpg`)
   - `MM-DD-YYYY` (e.g., `01-15-2024_photo.jpg`)
3. **File Modification Time**: Uses file system modification date as fallback

## 📁 File Structure

```
homeassistant-day-of-photos/
├── local_photos_fetcher.py    # Local photos fetcher
├── local_photos_dag.py        # Airflow DAG
├── setup_local_photos.py      # Setup and testing script
├── requirements.txt           # Python dependencies
├── README_LOCAL_PHOTOS.md     # This file
└── test_images/               # Test output directory
```

## 🔄 Daily Operation

Once deployed, the system will:

1. **4:00 AM daily**: Airflow triggers the DAG
2. **Photo search**: Scans your local photo directory recursively
3. **Date matching**: Finds photos from the same day across N years
4. **Copy photos**: Copies matching photos to the output directory
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

## 🔧 Troubleshooting

### Directory Access Issues

If the system can't access your photo directory:

1. **Check permissions**: Ensure Airflow can read the source directory
2. **Verify path**: Make sure the path is correct and accessible
3. **Test manually**: Run the fetcher outside of Airflow first

### No Photos Found

If no photos are found:

1. **Check date formats**: Verify your photos have dates in EXIF or filenames
2. **Test date detection**: Run with verbose logging to see date extraction
3. **Verify file types**: Ensure photos are in supported formats

### Airflow Issues

If the DAG doesn't run:

1. **Check Airflow logs**: `airflow tasks logs local_photos_day_photos fetch_local_photos`
2. **Verify file paths**: Ensure all paths are correct and accessible
3. **Test manually**: `airflow dags test local_photos_day_photos 2024-01-01`

## 📊 Monitoring

Monitor the DAG execution:

- **Airflow UI**: Check DAG runs and task logs
- **File system**: Monitor the output directory for new photos
- **Logs**: Check Airflow task logs for detailed information

## 🔒 Security Notes

- All processing happens locally - no data leaves your system
- No authentication credentials required
- No network access needed for photo processing
- File permissions should be set appropriately for your environment

## 🆘 Support

If you encounter issues:

1. **Check the logs** for specific error messages
2. **Test with the setup script** first
3. **Verify your photo directory** structure and permissions
4. **Ensure photos have dates** in EXIF data or filenames
5. **Check file formats** are supported

## 🔄 Migration from Cloud Solutions

If you're migrating from iCloud or Google Photos:

1. **No authentication setup** - Much simpler configuration
2. **No network dependencies** - Works offline
3. **Faster execution** - No download delays
4. **Same output format** - Compatible with existing Home Assistant setup
5. **Better privacy** - No cloud data transfer

## 🚀 Advantages Summary

| Feature | iCloud | Google Photos | Local Photos |
|---------|--------|---------------|--------------|
| 2FA Setup | Complex, device-dependent | OAuth complexity | None required |
| Authentication | App-specific passwords | OAuth tokens | File system access |
| Network Required | Yes | Yes | No |
| API Rate Limits | Yes | Yes | No |
| Data Privacy | Cloud storage | Cloud storage | Local only |
| Execution Speed | Network dependent | Network dependent | Instant |
| Setup Complexity | High | Medium | Low |
| Reliability | Variable | Good | Excellent |

## 📝 Photo Organization Tips

For best results, organize your photos in one of these ways:

### **Date-based directories**:
```
Photos/
├── 2024/
│   ├── 01/
│   │   ├── 15/
│   │   └── 16/
│   └── 02/
└── 2023/
    └── 12/
```

### **Flat structure with dated filenames**:
```
Photos/
├── 2024-01-15_vacation.jpg
├── 2024-01-15_family.jpg
└── 2023-12-25_christmas.jpg
```

### **Any structure with EXIF dates**:
The system will work with any organization as long as photos have EXIF date data.

---

**This local photos solution provides the most reliable and privacy-focused approach for fetching "on this day" photos, completely eliminating the complexity and limitations of cloud-based solutions.** 