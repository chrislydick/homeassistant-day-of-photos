# Troubleshooting DAG Loading Issues

## Common Reasons Why DAGs Don't Load

### 1. **Import Errors**
The most common cause is import errors in the DAG file.

**Check for:**
- Missing dependencies in `requirements.txt`
- Syntax errors in Python files
- Missing files that are being imported

**Test with:**
```bash
# Test if the DAG file can be imported
python -c "import onedrive_photos_dag; print('DAG imports successfully')"
```

### 2. **File Permissions**
Airflow needs to read the DAG files.

**Check:**
```bash
ls -la /path/to/airflow/dags/onedrive_photos_dag.py
ls -la /path/to/airflow/dags/onedrive_photos_fetcher.py
```

**Fix:**
```bash
chmod 644 /path/to/airflow/dags/onedrive_photos_dag.py
chmod 644 /path/to/airflow/dags/onedrive_photos_fetcher.py
```

### 3. **Airflow Configuration**
Check if Airflow is configured to scan the correct directory.

**Check:**
```bash
# In airflow.cfg or environment variables
echo $AIRFLOW_HOME
echo $DAGS_FOLDER
```

### 4. **DAG File Syntax**
Check for syntax errors in the DAG file.

**Test:**
```bash
python -m py_compile onedrive_photos_dag.py
python -m py_compile onedrive_photos_fetcher.py
```

### 5. **Missing Dependencies**
Install required packages on the Airflow machine.

**Install:**
```bash
pip install -r requirements.txt
```

### 6. **Airflow Logs**
Check Airflow logs for specific error messages.

**Check logs:**
```bash
# Look for DAG loading errors
tail -f /path/to/airflow/logs/scheduler/*.log
tail -f /path/to/airflow/logs/webserver/*.log
```

## Step-by-Step Debugging

### Step 1: Test Basic DAG Loading
Copy the `test_dag.py` file to your Airflow dags folder and see if it loads.

### Step 2: Test Import
On the Airflow machine, try importing the modules:
```bash
cd /path/to/airflow/dags/
python -c "from onedrive_photos_fetcher import fetch_onedrive_photos_airflow; print('Import works')"
```

### Step 3: Check Dependencies
Verify all required packages are installed:
```bash
pip list | grep -E "(requests|oauth|dotenv)"
```

### Step 4: Restart Airflow Services
Sometimes a restart is needed:
```bash
# Restart scheduler
airflow scheduler --stop
airflow scheduler

# Restart webserver
airflow webserver --stop
airflow webserver
```

## Quick Fixes

### Fix 1: Update DAG File
The DAG file has been updated with:
- Better error handling for imports
- Fixed `schedule_interval` parameter
- Environment variable support

### Fix 2: Check File Locations
Make sure both files are in the same directory:
```
/path/to/airflow/dags/
├── onedrive_photos_dag.py
├── onedrive_photos_fetcher.py
├── .env (sensitive)
└── onedrive_token.pickle (sensitive)
```

### Fix 3: Set Environment Variables
Set these in your Airflow environment:
```bash
export ONEDRIVE_OUTPUT_DIR="/actual/path/to/output"
export ONEDRIVE_TOKEN_FILE="/actual/path/to/airflow/dags/onedrive_token.pickle"
export ONEDRIVE_PHOTOS_FOLDER="Pictures"
```

## Expected Behavior

After fixing the issues, you should see:
1. DAG `onedrive_day_photos` appears in Airflow UI
2. DAG is paused by default
3. No import errors in logs
4. DAG can be unpaused and triggered manually

## Still Not Working?

If the DAG still doesn't load:
1. Check Airflow logs for specific error messages
2. Try the test DAG first to isolate the issue
3. Verify all files are in the correct location
4. Ensure all dependencies are installed
5. Restart Airflow services 