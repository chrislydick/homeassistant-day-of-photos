# Archived Airflow Code

This directory contains the original Airflow DAG implementation that was replaced by the standalone script approach.

## Files Archived

- `onedrive_photos_dag.py` - Original Airflow DAG file
- `onedrive_photos_fetcher.py` - Original OneDrive fetcher module for Airflow
- `setup_airflow.py` - Airflow setup and configuration script
- `requirements.txt` - Original requirements for Airflow deployment
- `SET_DAGS_FOLDER_PERSISTENT.md` - Documentation for setting up persistent DAGs folder

## Migration to Standalone Script

The Airflow implementation was replaced with a standalone Python script approach for the following reasons:

1. **Simplified Deployment** - No need for Airflow infrastructure
2. **Easier Maintenance** - Single script with all functionality
3. **Better Token Management** - Enhanced authentication handling
4. **Cron Integration** - Direct integration with system cron
5. **Reduced Complexity** - Fewer moving parts and dependencies

## Current Implementation

The current implementation uses:
- `onedrive_photos_script.py` - Main standalone script
- `onedrive_photos_script_enhanced.py` - Enhanced version with better token management
- `requirements_standalone.txt` - Simplified dependencies
- `setup_crontab.sh` - Cron job setup script

## If You Need to Reference the Airflow Code

The original Airflow implementation is preserved here for reference. Key differences:

- **Authentication**: Airflow used environment variables, standalone uses .env files
- **Token Management**: Airflow had basic token handling, standalone has enhanced token management
- **Deployment**: Airflow required DAG folder setup, standalone is a single script
- **Scheduling**: Airflow used DAG scheduling, standalone uses cron

## Migration Notes

The core OneDrive API logic was preserved and enhanced in the standalone scripts. The main changes were:

1. Removed Airflow-specific imports and decorators
2. Enhanced token management and error handling
3. Added command-line argument parsing
4. Improved logging and user feedback
5. Added HEIC conversion and cleanup features
