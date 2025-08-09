# Airflow Emergency Checklist - No DAGs Loading

## 🚨 **CRITICAL: Run These Commands on Your Airflow Machine**

### **Step 1: Basic Airflow Status**
```bash
# Check if Airflow is actually running
ps aux | grep airflow

# Check Airflow version
airflow version

# Check Airflow home
echo $AIRFLOW_HOME
```

### **Step 2: Check DAGS_FOLDER**
```bash
# Check DAGS_FOLDER environment variable
echo $DAGS_FOLDER

# Check airflow.cfg
cat $AIRFLOW_HOME/airflow.cfg | grep dags_folder

# List files in DAGS_FOLDER
ls -la $DAGS_FOLDER
```

### **Step 3: Test File Permissions**
```bash
# Check if Airflow can read the files
ls -la $DAGS_FOLDER/*.py

# Fix permissions if needed
chmod 644 $DAGS_FOLDER/*.py
```

### **Step 4: Test Python Import**
```bash
# Go to DAGS_FOLDER
cd $DAGS_FOLDER

# Test if Python can import the files
python -c "import ultimate_airflow_test; print('✅ Ultimate test imports')"
python -c "import simple_test_dag; print('✅ Simple test imports')"
python -c "import onedrive_photos_dag; print('✅ OneDrive DAG imports')"
```

### **Step 5: Check Airflow CLI**
```bash
# List all DAGs
airflow dags list

# Test DAG parsing
airflow dags test ultimate_test 2024-01-01
```

### **Step 6: Check Airflow Logs**
```bash
# Check recent scheduler logs
tail -50 $AIRFLOW_HOME/logs/scheduler/*.log

# Check for specific errors
grep -i "error\|exception\|traceback" $AIRFLOW_HOME/logs/scheduler/*.log | tail -20
```

### **Step 7: Restart Airflow Services**
```bash
# Stop all Airflow processes
pkill -f airflow

# Wait a moment
sleep 5

# Start services
airflow webserver --daemon
airflow scheduler --daemon

# Check if they're running
ps aux | grep airflow
```

## 🔍 **Common Issues and Quick Fixes**

### **Issue 1: DAGS_FOLDER Not Set**
```bash
# Set DAGS_FOLDER
export DAGS_FOLDER="/path/to/your/dags"

# Or edit airflow.cfg
# Find: dags_folder = /path/to/airflow/dags
# Change to your actual path
```

### **Issue 2: Database Problems**
```bash
# Check database
airflow db check

# Reset if needed (WARNING: Deletes all data)
airflow db reset
airflow db init
```

### **Issue 3: Python Environment**
```bash
# Check Python path
which python
python --version

# Check if Airflow uses the right Python
airflow info | grep python
```

### **Issue 4: File Encoding**
```bash
# Check file encoding
file $DAGS_FOLDER/*.py

# Should show: ASCII text or UTF-8 Unicode text
```

## 🎯 **Expected Results**

After running the checklist, you should see:

1. **Airflow processes running:**
   ```
   airflow scheduler
   airflow webserver
   ```

2. **DAGS_FOLDER contains files:**
   ```
   ultimate_airflow_test.py
   simple_test_dag.py
   onedrive_photos_dag.py
   ```

3. **Python imports work:**
   ```
   ✅ Ultimate test imports
   ✅ Simple test imports
   ✅ OneDrive DAG imports
   ```

4. **Airflow CLI shows DAGs:**
   ```
   ultimate_test
   simple_test
   onedrive_day_photos
   ```

## 🆘 **If Still No DAGs**

If none of the above work:

1. **Check if Airflow is properly installed:**
   ```bash
   pip list | grep airflow
   ```

2. **Try a fresh Airflow installation:**
   ```bash
   pip uninstall apache-airflow
   pip install apache-airflow==2.10.2
   airflow db init
   ```

3. **Check system resources:**
   ```bash
   df -h  # Check disk space
   free -h  # Check memory
   ```

4. **Check for conflicting Python environments:**
   ```bash
   which python
   which airflow
   ```

## 📞 **Share These Results**

Run these commands and share the output:

```bash
# 1. Airflow status
ps aux | grep airflow
airflow version

# 2. DAGS_FOLDER check
echo $DAGS_FOLDER
ls -la $DAGS_FOLDER

# 3. Import test
cd $DAGS_FOLDER
python -c "import ultimate_airflow_test"

# 4. Airflow CLI test
airflow dags list

# 5. Recent errors
tail -20 $AIRFLOW_HOME/logs/scheduler/*.log
```

This will help identify the exact issue! 