# Setting DAGS_FOLDER Persistently for Airflow

## 🎯 **The Problem**
Your `DAGS_FOLDER` environment variable is blank, so Airflow doesn't know where to look for DAGs.

## 🔧 **Solution: Set DAGS_FOLDER Persistently**

### **Step 1: Find Your Airflow Home**
```bash
# Check where Airflow is installed
airflow info | grep AIRFLOW_HOME

# Or check common locations
echo $AIRFLOW_HOME
ls -la ~/.airflow/
ls -la /opt/airflow/
```

### **Step 2: Choose Your DAGS_FOLDER Location**

You have several options:

#### **Option A: Use Airflow Home Directory (Recommended)**
```bash
# If AIRFLOW_HOME is set, use its dags subdirectory
export DAGS_FOLDER="$AIRFLOW_HOME/dags"

# Create the directory if it doesn't exist
mkdir -p "$DAGS_FOLDER"
```

#### **Option B: Use a Custom Directory**
```bash
# Set to a custom location
export DAGS_FOLDER="/path/to/your/custom/dags"

# Create the directory
mkdir -p "$DAGS_FOLDER"
```

#### **Option C: Use User Home Directory**
```bash
# Use a directory in your home
export DAGS_FOLDER="$HOME/airflow_dags"

# Create the directory
mkdir -p "$DAGS_FOLDER"
```

### **Step 3: Set DAGS_FOLDER Persistently**

#### **Method 1: Environment Variable (Recommended)**
```bash
# Add to your shell profile
echo 'export DAGS_FOLDER="/path/to/your/dags"' >> ~/.bashrc
echo 'export DAGS_FOLDER="/path/to/your/dags"' >> ~/.profile

# Reload the profile
source ~/.bashrc
source ~/.profile

# Verify it's set
echo $DAGS_FOLDER
```

#### **Method 2: Edit airflow.cfg (Alternative)**
```bash
# Find your airflow.cfg
find / -name "airflow.cfg" 2>/dev/null

# Edit the file
nano $AIRFLOW_HOME/airflow.cfg

# Find the line: dags_folder = /path/to/airflow/dags
# Change it to: dags_folder = /path/to/your/dags
```

#### **Method 3: System-wide Environment (For Production)**
```bash
# Create a system-wide environment file
sudo nano /etc/environment

# Add this line:
DAGS_FOLDER=/path/to/your/dags

# Or create a profile file
sudo nano /etc/profile.d/airflow.sh

# Add these lines:
#!/bin/bash
export DAGS_FOLDER="/path/to/your/dags"
export AIRFLOW_HOME="/path/to/airflow"

# Make it executable
sudo chmod +x /etc/profile.d/airflow.sh
```

### **Step 4: Verify the Setup**
```bash
# Check if DAGS_FOLDER is set
echo $DAGS_FOLDER

# Check if the directory exists
ls -la "$DAGS_FOLDER"

# Test with Airflow
airflow info | grep DAGS_FOLDER
```

### **Step 5: Copy Your DAG Files**
```bash
# Copy your DAG files to the DAGS_FOLDER
cp onedrive_photos_dag.py "$DAGS_FOLDER/"
cp onedrive_photos_fetcher.py "$DAGS_FOLDER/"
cp ultimate_airflow_test.py "$DAGS_FOLDER/"
cp simple_test_dag.py "$DAGS_FOLDER/"

# Copy sensitive files
cp .env "$DAGS_FOLDER/"
cp onedrive_token.pickle "$DAGS_FOLDER/"

# Verify files are there
ls -la "$DAGS_FOLDER/"
```

### **Step 6: Restart Airflow**
```bash
# Stop Airflow services
pkill -f airflow

# Wait a moment
sleep 5

# Start Airflow services
airflow webserver --daemon
airflow scheduler --daemon

# Check if they're running
ps aux | grep airflow
```

### **Step 7: Test DAG Loading**
```bash
# List DAGs
airflow dags list

# Test DAG parsing
airflow dags test ultimate_test 2024-01-01
```

## 📋 **Complete Setup Example**

Here's a complete example assuming you want to use `/opt/airflow/dags`:

```bash
# 1. Set environment variables
export AIRFLOW_HOME="/opt/airflow"
export DAGS_FOLDER="/opt/airflow/dags"

# 2. Create directories
sudo mkdir -p /opt/airflow/dags
sudo mkdir -p /opt/airflow/logs
sudo mkdir -p /opt/airflow/plugins

# 3. Set permissions
sudo chown -R $USER:$USER /opt/airflow
chmod 755 /opt/airflow/dags

# 4. Make persistent
echo 'export AIRFLOW_HOME="/opt/airflow"' >> ~/.bashrc
echo 'export DAGS_FOLDER="/opt/airflow/dags"' >> ~/.bashrc
source ~/.bashrc

# 5. Copy files
cp *.py /opt/airflow/dags/
cp .env /opt/airflow/dags/
cp *.pickle /opt/airflow/dags/

# 6. Restart Airflow
pkill -f airflow
sleep 5
airflow webserver --daemon
airflow scheduler --daemon

# 7. Test
airflow dags list
```

## 🎯 **Expected Results**

After setting DAGS_FOLDER persistently:

1. **Environment variable is set:**
   ```bash
   echo $DAGS_FOLDER
   # Should show: /path/to/your/dags
   ```

2. **Airflow recognizes the setting:**
   ```bash
   airflow info | grep DAGS_FOLDER
   # Should show the correct path
   ```

3. **DAGs appear in the list:**
   ```bash
   airflow dags list
   # Should show your DAGs
   ```

4. **DAGs appear in the UI:**
   - Go to Airflow web UI
   - See your DAGs listed

## 🚨 **Troubleshooting**

### **If DAGS_FOLDER is still blank after setting it:**
```bash
# Check if it's set in current session
echo $DAGS_FOLDER

# Check if it's in your profile
grep DAGS_FOLDER ~/.bashrc

# Reload your profile
source ~/.bashrc

# Restart your terminal session
```

### **If Airflow still doesn't see DAGs:**
```bash
# Check if files are in the right place
ls -la "$DAGS_FOLDER"

# Check file permissions
chmod 644 "$DAGS_FOLDER"/*.py

# Restart Airflow completely
pkill -f airflow
sleep 10
airflow webserver --daemon
airflow scheduler --daemon
```

## 📞 **Quick Test**

Run this to verify everything is working:

```bash
# 1. Check environment
echo "DAGS_FOLDER: $DAGS_FOLDER"
echo "AIRFLOW_HOME: $AIRFLOW_HOME"

# 2. Check files
ls -la "$DAGS_FOLDER"

# 3. Test Airflow
airflow dags list

# 4. Check logs
tail -20 $AIRFLOW_HOME/logs/scheduler/*.log
```

This should fix your DAG loading issue! 