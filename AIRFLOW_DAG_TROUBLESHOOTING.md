# Airflow DAG Not Appearing in GUI - Troubleshooting Guide

## 🔍 **Step-by-Step Diagnosis**

### **Step 1: Check if Files Are in the Right Location**

On your Airflow machine, verify the files are in the correct directory:

```bash
# Check your Airflow dags directory
ls -la /path/to/airflow/dags/

# Should show:
# - onedrive_photos_dag.py
# - onedrive_photos_fetcher.py
# - .env (if using)
# - onedrive_token.pickle
```

### **Step 2: Check File Permissions**

Airflow needs to read the files:

```bash
# Check permissions
ls -la /path/to/airflow/dags/onedrive_photos_dag.py
ls -la /path/to/airflow/dags/onedrive_photos_fetcher.py

# Fix if needed
chmod 644 /path/to/airflow/dags/onedrive_photos_dag.py
chmod 644 /path/to/airflow/dags/onedrive_photos_fetcher.py
```

### **Step 3: Test Import on Airflow Machine**

```bash
# Go to dags directory
cd /path/to/airflow/dags/

# Test if the DAG can be imported
python -c "import onedrive_photos_dag; print('✅ DAG imports successfully')"

# Test if the fetcher can be imported
python -c "from onedrive_photos_fetcher import fetch_onedrive_photos_airflow; print('✅ Fetcher imports successfully')"
```

### **Step 4: Check Airflow Logs**

Look for specific error messages:

```bash
# Check scheduler logs
tail -f /path/to/airflow/logs/scheduler/*.log | grep -i "onedrive"

# Check webserver logs
tail -f /path/to/airflow/logs/webserver/*.log | grep -i "error"

# Check for import errors
grep -i "import" /path/to/airflow/logs/scheduler/*.log | tail -20
```

### **Step 5: Check Dependencies**

Verify all required packages are installed:

```bash
# Check if required packages are installed
pip list | grep -E "(requests|oauth|dotenv)"

# Install missing dependencies
pip install requests python-dotenv requests-oauthlib
```

### **Step 6: Restart Airflow Services**

Sometimes a restart is needed:

```bash
# Stop services
airflow scheduler --stop
airflow webserver --stop

# Start services
airflow scheduler
airflow webserver
```

## 🚨 **Common Issues and Fixes**

### **Issue 1: Import Errors**
**Symptoms:** DAG doesn't appear, import errors in logs
**Fix:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install individually
pip install requests python-dotenv requests-oauthlib
```

### **Issue 2: Syntax Errors**
**Symptoms:** DAG doesn't appear, syntax errors in logs
**Fix:**
```bash
# Test syntax
python -m py_compile onedrive_photos_dag.py
python -m py_compile onedrive_photos_fetcher.py
```

### **Issue 3: File Not Found**
**Symptoms:** "No module named 'onedrive_photos_fetcher'" error
**Fix:**
```bash
# Ensure both files are in the same directory
ls -la /path/to/airflow/dags/
# Should show both .py files
```

### **Issue 4: Airflow Configuration**
**Symptoms:** DAGs not being scanned
**Fix:**
```bash
# Check DAGS_FOLDER setting
echo $DAGS_FOLDER
# or check airflow.cfg for dags_folder setting
```

### **Issue 5: DAG is Paused**
**Symptoms:** DAG appears but is paused (grayed out)
**Fix:** Unpause the DAG in the Airflow UI

## 🔧 **Quick Diagnostic Commands**

### **Test Basic DAG Loading**
```bash
# Create a simple test DAG
cat > /path/to/airflow/dags/test_simple.py << 'EOF'
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def test_func():
    print("Test works!")

dag = DAG(
    dag_id="test_simple",
    start_date=datetime(2024, 1, 1),
    schedule="0 4 * * *",
)

task = PythonOperator(
    task_id="test_task",
    python_callable=test_func,
    dag=dag,
)
EOF

# Check if test DAG appears in UI
```

### **Check Airflow Status**
```bash
# Check if Airflow is running
ps aux | grep airflow

# Check Airflow version
airflow version

# Check Airflow home
echo $AIRFLOW_HOME
```

### **Force DAG Refresh**
```bash
# Restart scheduler to force DAG refresh
airflow scheduler --stop
sleep 5
airflow scheduler
```

## 📋 **Checklist for DAG to Appear**

- [ ] Files are in the correct `/path/to/airflow/dags/` directory
- [ ] Files have correct permissions (644)
- [ ] No syntax errors in Python files
- [ ] All dependencies are installed
- [ ] Airflow scheduler is running
- [ ] No import errors in logs
- [ ] DAG ID is unique (`onedrive_day_photos`)
- [ ] DAG file ends with `.py` extension

## 🎯 **Expected Behavior**

After fixing issues, you should see:
1. DAG `onedrive_day_photos` appears in Airflow UI
2. DAG is paused by default (grayed out)
3. No errors in scheduler logs
4. DAG can be unpaused and triggered manually

## 🆘 **Still Not Working?**

If the DAG still doesn't appear:

1. **Check the exact error** in Airflow logs
2. **Try the test DAG** first to isolate the issue
3. **Verify Airflow version** - some syntax changed between versions
4. **Check file encoding** - ensure files are UTF-8
5. **Restart all Airflow services** completely

## 📞 **Get Specific Error Messages**

Run these commands on your Airflow machine and share the output:

```bash
# 1. Check if files exist
ls -la /path/to/airflow/dags/onedrive_photos*

# 2. Test import
cd /path/to/airflow/dags/
python -c "import onedrive_photos_dag"

# 3. Check recent scheduler logs
tail -50 /path/to/airflow/logs/scheduler/*.log | grep -i "error\|exception\|traceback"

# 4. Check Airflow version
airflow version
``` 