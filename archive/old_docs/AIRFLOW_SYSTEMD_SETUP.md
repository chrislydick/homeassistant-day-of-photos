# Airflow with systemctl - Setting DAGS_FOLDER

## 🎯 **The Problem**
When Airflow runs via systemctl, it doesn't inherit your shell environment variables. You need to configure the systemd service.

## 🔍 **Step 1: Find Your Airflow Service**

```bash
# Check if Airflow services are running via systemctl
systemctl status airflow*

# List all Airflow-related services
systemctl list-units --type=service | grep airflow

# Common service names:
# - airflow-webserver
# - airflow-scheduler
# - airflow-worker
# - apache-airflow-webserver
# - apache-airflow-scheduler
```

## 🔧 **Step 2: Check Current Service Configuration**

```bash
# Check the service file location
systemctl show airflow-webserver | grep FragmentPath

# Or find the service file
find /etc/systemd/system /lib/systemd/system -name "*airflow*" 2>/dev/null

# View the service file
sudo cat /etc/systemd/system/airflow-webserver.service
sudo cat /etc/systemd/system/airflow-scheduler.service
```

## 🚀 **Step 3: Configure DAGS_FOLDER in systemd**

### **Method 1: Edit Service Files (Recommended)**

```bash
# Edit the webserver service
sudo nano /etc/systemd/system/airflow-webserver.service

# Edit the scheduler service
sudo nano /etc/systemd/system/airflow-scheduler.service
```

**Add these lines to both service files:**

```ini
[Unit]
Description=Airflow webserver daemon
After=network.target

[Service]
Type=simple
User=airflow
Group=airflow
Environment="AIRFLOW_HOME=/opt/airflow"
Environment="DAGS_FOLDER=/opt/airflow/dags"
ExecStart=/usr/local/bin/airflow webserver
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### **Method 2: Create Environment File**

```bash
# Create environment file
sudo nano /etc/default/airflow

# Add these lines:
AIRFLOW_HOME=/opt/airflow
DAGS_FOLDER=/opt/airflow/dags
```

**Then modify service files to use the environment file:**

```ini
[Service]
EnvironmentFile=/etc/default/airflow
ExecStart=/usr/local/bin/airflow webserver
```

### **Method 3: Use Environment Directives**

```bash
# Edit service files and add Environment directives
sudo nano /etc/systemd/system/airflow-webserver.service
sudo nano /etc/systemd/system/airflow-scheduler.service
```

**Add these lines in the [Service] section:**

```ini
[Service]
Environment="AIRFLOW_HOME=/opt/airflow"
Environment="DAGS_FOLDER=/opt/airflow/dags"
Environment="AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags"
```

## 📁 **Step 4: Create DAGS_FOLDER Directory**

```bash
# Create the directory
sudo mkdir -p /opt/airflow/dags

# Set ownership (replace 'airflow' with your Airflow user)
sudo chown -R airflow:airflow /opt/airflow
# Or if running as your user:
sudo chown -R $USER:$USER /opt/airflow

# Set permissions
sudo chmod 755 /opt/airflow/dags
```

## 📋 **Step 5: Copy Your DAG Files**

```bash
# Copy DAG files to the DAGS_FOLDER
sudo cp onedrive_photos_dag.py /opt/airflow/dags/
sudo cp onedrive_photos_fetcher.py /opt/airflow/dags/
sudo cp ultimate_airflow_test.py /opt/airflow/dags/
sudo cp simple_test_dag.py /opt/airflow/dags/

# Copy sensitive files
sudo cp .env /opt/airflow/dags/
sudo cp onedrive_token.pickle /opt/airflow/dags/

# Set correct ownership
sudo chown -R airflow:airflow /opt/airflow/dags/
# Or for your user:
sudo chown -R $USER:$USER /opt/airflow/dags/

# Set permissions
sudo chmod 644 /opt/airflow/dags/*.py
```

## 🔄 **Step 6: Reload and Restart Services**

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Restart Airflow services
sudo systemctl restart airflow-webserver
sudo systemctl restart airflow-scheduler

# Check service status
sudo systemctl status airflow-webserver
sudo systemctl status airflow-scheduler

# Check if services are running
sudo systemctl is-active airflow-webserver
sudo systemctl is-active airflow-scheduler
```

## 🧪 **Step 7: Test the Configuration**

```bash
# Check if environment variables are set in the service
sudo systemctl show airflow-webserver | grep Environment

# Check if DAGS_FOLDER is accessible
sudo -u airflow ls -la /opt/airflow/dags

# Test DAG loading
sudo -u airflow airflow dags list

# Check logs for any errors
sudo journalctl -u airflow-webserver -f
sudo journalctl -u airflow-scheduler -f
```

## 🔍 **Step 8: Verify Everything Works**

```bash
# Check if DAGs are loaded
sudo -u airflow airflow dags list

# Test a specific DAG
sudo -u airflow airflow dags test ultimate_test 2024-01-01

# Check Airflow info
sudo -u airflow airflow info | grep DAGS_FOLDER
```

## 🚨 **Troubleshooting**

### **If Services Won't Start:**

```bash
# Check service logs
sudo journalctl -u airflow-webserver -n 50
sudo journalctl -u airflow-scheduler -n 50

# Check service configuration
sudo systemctl cat airflow-webserver
sudo systemctl cat airflow-scheduler

# Test service manually
sudo -u airflow airflow webserver --help
```

### **If DAGS_FOLDER Still Not Set:**

```bash
# Check if environment is set in running process
sudo systemctl show airflow-webserver | grep Environment

# Check if the directory exists and has correct permissions
ls -la /opt/airflow/dags

# Check if Airflow user can access the directory
sudo -u airflow ls -la /opt/airflow/dags
```

### **If DAGs Still Don't Load:**

```bash
# Check Airflow logs
sudo tail -f /opt/airflow/logs/scheduler/*.log

# Check if files are in the right place
sudo ls -la /opt/airflow/dags/

# Test import manually
sudo -u airflow python -c "import sys; sys.path.append('/opt/airflow/dags'); import ultimate_airflow_test"
```

## 📋 **Complete Example Service File**

Here's a complete example for `/etc/systemd/system/airflow-webserver.service`:

```ini
[Unit]
Description=Airflow webserver daemon
After=network.target

[Service]
Type=simple
User=airflow
Group=airflow
Environment="AIRFLOW_HOME=/opt/airflow"
Environment="DAGS_FOLDER=/opt/airflow/dags"
Environment="AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags"
Environment="AIRFLOW__CORE__EXECUTOR=LocalExecutor"
Environment="AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db"
Environment="AIRFLOW__CORE__FERNET_KEY="
Environment="AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True"
Environment="AIRFLOW__CORE__LOAD_EXAMPLES=False"
ExecStart=/usr/local/bin/airflow webserver
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

## 🎯 **Expected Results**

After configuration:

1. **Services start successfully:**
   ```bash
   sudo systemctl status airflow-webserver
   # Should show: active (running)
   ```

2. **Environment variables are set:**
   ```bash
   sudo systemctl show airflow-webserver | grep DAGS_FOLDER
   # Should show the path
   ```

3. **DAGs are loaded:**
   ```bash
   sudo -u airflow airflow dags list
   # Should show your DAGs
   ```

4. **Web UI shows DAGs:**
   - Go to Airflow web interface
   - See your DAGs listed

## 📞 **Quick Verification**

Run these commands to verify everything is working:

```bash
# 1. Check service status
sudo systemctl status airflow-webserver airflow-scheduler

# 2. Check environment
sudo systemctl show airflow-webserver | grep Environment

# 3. Check DAGs
sudo -u airflow airflow dags list

# 4. Check logs
sudo journalctl -u airflow-scheduler --no-pager | tail -20
```

This should fix your DAG loading issue with systemctl-managed Airflow! 