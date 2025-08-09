# Airflow - No DAGs Showing Up (Fundamental Issues)

## 🚨 **When NO DAGs Appear in Airflow UI**

If neither your OneDrive DAG nor the test DAG are showing up, this indicates a fundamental Airflow configuration problem.

## 🔍 **Step-by-Step Diagnosis**

### **Step 1: Check if Airflow is Running**

```bash
# Check if Airflow processes are running
ps aux | grep airflow

# Should show:
# - airflow scheduler
# - airflow webserver
# - airflow worker (if using Celery)
```

### **Step 2: Check Airflow Configuration**

```bash
# Check Airflow home directory
echo $AIRFLOW_HOME

# Check DAGS_FOLDER setting
echo $DAGS_FOLDER

# Check airflow.cfg file
cat $AIRFLOW_HOME/airflow.cfg | grep dags_folder
```

### **Step 3: Verify DAGs Directory**

```bash
# Check if the dags directory exists and has files
ls -la $DAGS_FOLDER

# Or check the default location
ls -la $AIRFLOW_HOME/dags/
```

### **Step 4: Check Airflow Version and Setup**

```bash
# Check Airflow version
airflow version

# Check Airflow home
airflow info

# Check if database is initialized
airflow db check
```

### **Step 5: Check Airflow Logs**

```bash
# Check scheduler logs for errors
tail -50 $AIRFLOW_HOME/logs/scheduler/*.log

# Check webserver logs
tail -50 $AIRFLOW_HOME/logs/webserver/*.log

# Look for specific errors
grep -i "error\|exception\|traceback" $AIRFLOW_HOME/logs/scheduler/*.log | tail -20
```

## 🚨 **Common Fundamental Issues**

### **Issue 1: Airflow Not Properly Installed**
**Symptoms:** No Airflow processes running
**Fix:**
```bash
# Install Airflow properly
pip install apache-airflow

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### **Issue 2: Wrong DAGS_FOLDER Configuration**
**Symptoms:** Airflow running but no DAGs found
**Fix:**
```bash
# Check current setting
echo $DAGS_FOLDER

# Set correct DAGS_FOLDER
export DAGS_FOLDER="/path/to/your/dags"

# Or edit airflow.cfg
# Find the line: dags_folder = /path/to/airflow/dags
# Change it to your actual dags folder path
```

### **Issue 3: Database Issues**
**Symptoms:** Airflow starts but DAGs don't load
**Fix:**
```bash
# Check database
airflow db check

# Reset database if needed (WARNING: This will delete all data)
airflow db reset

# Reinitialize
airflow db init
```

### **Issue 4: Permission Issues**
**Symptoms:** Files exist but Airflow can't read them
**Fix:**
```bash
# Check file permissions
ls -la $DAGS_FOLDER/

# Fix permissions
chmod 644 $DAGS_FOLDER/*.py
chown -R airflow:airflow $DAGS_FOLDER/  # If using system user
```

### **Issue 5: Python Environment Issues**
**Symptoms:** Import errors or missing modules
**Fix:**
```bash
# Check Python path
which python
python --version

# Check if Airflow is using the right Python
airflow info | grep python

# Install dependencies in the right environment
pip install requests python-dotenv requests-oauthlib
```

## 🔧 **Quick Fixes**

### **Fix 1: Restart Everything**
```bash
# Stop all Airflow services
pkill -f airflow

# Start fresh
airflow webserver --daemon
airflow scheduler --daemon
```

### **Fix 2: Check DAG Scanning**
```bash
# Test DAG parsing manually
airflow dags test onedrive_day_photos 2024-01-01

# List all DAGs
airflow dags list
```

### **Fix 3: Create Minimal Test**
```bash
# Create a very simple test DAG
cat > $DAGS_FOLDER/minimal_test.py << 'EOF'
from airflow import DAG
from datetime import datetime

dag = DAG(
    dag_id="minimal_test",
    start_date=datetime(2024, 1, 1),
    schedule="0 4 * * *",
)
EOF

# Check if it appears
airflow dags list | grep minimal_test
```

## 📋 **Complete Reset Procedure**

If nothing else works, try a complete reset:

```bash
# 1. Stop all Airflow services
pkill -f airflow

# 2. Backup your dags folder
cp -r $DAGS_FOLDER /tmp/dags_backup

# 3. Reset Airflow
airflow db reset

# 4. Reinitialize
airflow db init

# 5. Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# 6. Restore your dags
cp /tmp/dags_backup/* $DAGS_FOLDER/

# 7. Start services
airflow webserver --daemon
airflow scheduler --daemon
```

## 🎯 **Expected Results**

After fixing the issues, you should see:

1. **Airflow processes running:**
   ```bash
   ps aux | grep airflow
   # Should show scheduler and webserver
   ```

2. **DAGs directory accessible:**
   ```bash
   ls -la $DAGS_FOLDER/
   # Should show your .py files
   ```

3. **DAGs listed:**
   ```bash
   airflow dags list
   # Should show your DAGs
   ```

4. **Web UI accessible:**
   - Go to http://localhost:8080
   - Login with admin/admin
   - See DAGs in the UI

## 🆘 **Still Not Working?**

If you still don't see any DAGs:

1. **Check if Airflow is actually running:**
   ```bash
   ps aux | grep airflow
   ```

2. **Check the exact error messages:**
   ```bash
   tail -100 $AIRFLOW_HOME/logs/scheduler/*.log
   ```

3. **Verify your Airflow installation:**
   ```bash
   airflow version
   airflow info
   ```

4. **Try a completely fresh Airflow installation**

Share the output of these commands and I can help identify the specific issue! 