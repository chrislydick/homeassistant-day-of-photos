# Archive - Old Implementations

This folder contains the previous implementations that are no longer actively used.

## Contents

### Old OneDrive Implementation
- `onedrive_photos_fetcher.py` - Original OneDrive fetcher with O365 library issues

### Google Photos Implementation
- `google_photos_fetcher.py` - Google Photos fetcher
- `google_photos_dag.py` - Google Photos DAG
- `setup_google_photos.py` - Google Photos setup script

### iCloud Implementation
- `icloud_photo_fetcher.py` - iCloud photo fetcher
- `icloud_dag.py` - iCloud DAG
- `icloud_photos_dag.py` - Alternative iCloud DAG

### Dropbox Implementation
- `dropbox_photos_fetcher.py` - Dropbox photos fetcher

### Local Photos Implementation
- `local_photos_dag.py` - Local photos DAG
- `setup_local_photos.py` - Local photos setup script

## Current Active Implementation

The current working implementation is in the root directory:
- `onedrive_photos_fetcher.py` - Simplified OneDrive fetcher with reliable OAuth
- `onedrive_photos_dag.py` - OneDrive DAG
- `setup_onedrive.py` - OneDrive setup script

## Why These Were Archived

- **OneDrive**: Original implementation had OAuth state mismatch issues
- **Google Photos**: Not the primary focus (OneDrive was chosen)
- **iCloud**: Had 2FA issues on Linux systems
- **Dropbox**: Not the primary focus
- **Local Photos**: Not the primary focus

The OneDrive implementation was chosen as the primary solution due to:
1. ✅ Reliable OAuth authentication
2. ✅ Good API stability
3. ✅ Easy integration with iCloud sync
4. ✅ No 2FA issues on Linux 