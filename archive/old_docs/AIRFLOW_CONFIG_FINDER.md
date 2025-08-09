# Finding Your Airflow Configuration

## 🔍 **How to Find Your Airflow Configuration**

### **Step 1: Check Environment Variables**
```bash
# Check AIRFLOW_HOME
echo $AIRFLOW_HOME

# Check DAGS_FOLDER
echo $DAGS_FOLDER
```

### **Step 2: Check Airflow Info**
```bash
# Get Airflow configuration info
airflow info

# This will show you:
# - AIRFLOW_HOME
# - DAGS_FOLDER
# - Python path
# - Database URL
```

### **Step 3: Check airflow.cfg File**
```bash
# Find the airflow.cfg file
find / -name "airflow.cfg" 2>/dev/null

# Or check common locations
ls -la ~/.airflow/airflow.cfg
ls -la /opt/airflow/airflow.cfg
ls -la /usr/local/airflow/airflow.cfg
```

### **Step 4: View airflow.cfg Contents**
```bash
# Once you find airflow.cfg, check the dags_folder setting
cat $AIRFLOW_HOME/airflow.cfg | grep dags_folder

# Or view the entire config
cat $AIRFLOW_HOME/airflow.cfg
```

## 📁 **Common Airflow Directory Locations**

### **Default Locations:**
```bash
# User home directory
~/.airflow/

# System-wide installation
/opt/airflow/

# Local installation
/usr/local/airflow/

# Docker container
/opt/airflow/
```

### **Check What's in Your Airflow Home:**
```bash
# List contents of AIRFLOW_HOME
ls -la $AIRFLOW_HOME

# Should show:
# - airflow.cfg
# - dags/ (directory)
# - logs/ (directory)
# - plugins/ (directory)
```

## 🎯 **Quick Commands to Find Your Setup**

### **Command 1: Find Airflow Home**
```bash
airflow info | grep "AIRFLOW_HOME"
```

### **Command 2: Find DAGS_FOLDER**
```bash
airflow info | grep "DAGS_FOLDER"
```

### **Command 3: Check Current DAGs Directory**
```bash
# List files in current DAGS_FOLDER
ls -la $DAGS_FOLDER

# Or check if it exists
echo "DAGS_FOLDER: $DAGS_FOLDER"
ls -la "$DAGS_FOLDER" 2>/dev/null || echo "Directory not found"
```

## 🔧 **If You Can't Find the Configuration**

### **Option 1: Check Running Airflow Processes**
```bash
# See where Airflow is running from
ps aux | grep airflow

# Look for the --config flag or AIRFLOW_HOME in the process
```

### **Option 2: Search for Airflow Files**
```bash
# Search for airflow.cfg
sudo find / -name "airflow.cfg" 2>/dev/null

# Search for dags directory
sudo find / -name "dags" -type d 2>/dev/null | grep airflow
```

### **Option 3: Check Package Installation**
```bash
# If installed via pip
pip show apache-airflow

# If installed via system package
which airflow
```

## 📋 **Expected Results**

After running these commands, you should see something like:

```bash
# Environment variables
AIRFLOW_HOME=/opt/airflow
DAGS_FOLDER=/opt/airflow/dags

# Directory contents
/opt/airflow/
├── airflow.cfg
├── dags/
│   ├── your_dag.py
│   └── ...
├── logs/
└── plugins/
```

## 🚨 **If DAGS_FOLDER is Not Set**

If `echo $DAGS_FOLDER` returns empty:

1. **Set it manually:**
   ```bash
   export DAGS_FOLDER="/path/to/your/dags"
   ```

2. **Add to your shell profile:**
   ```bash
   echo 'export DAGS_FOLDER="/path/to/your/dags"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Or edit airflow.cfg:**
   ```bash
   # Find the line: dags_folder = /path/to/airflow/dags
   # Change it to your actual path
   nano $AIRFLOW_HOME/airflow.cfg
   ```

## 📞 **Share Your Results**

Run these commands and share the output:

```bash
# 1. Environment variables
echo "AIRFLOW_HOME: $AIRFLOW_HOME"
echo "DAGS_FOLDER: $DAGS_FOLDER"

# 2. Airflow info
airflow info | grep -E "(AIRFLOW_HOME|DAGS_FOLDER)"

# 3. Directory contents
ls -la $AIRFLOW_HOME
ls -la $DAGS_FOLDER 2>/dev/null || echo "DAGS_FOLDER not found"

# 4. Find airflow.cfg
find / -name "airflow.cfg" 2>/dev/null | head -5
```

This will help us identify exactly where your Airflow is configured! 