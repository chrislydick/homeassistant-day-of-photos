# Deployment Checklist

## ✅ **Pre-Deployment Verification**

### **1. Test Authentication**
```bash
python setup_onedrive.py
```
- ✅ Authentication works
- ✅ Token is saved
- ✅ Photo search works (even if no photos found)

### **2. Verify Files to Commit**
```bash
# These should be committed to GitHub:
✅ onedrive_photos_fetcher.py
✅ onedrive_photos_dag.py
✅ setup_onedrive.py
✅ requirements.txt
✅ README_CURRENT.md
✅ CLOUD_ALTERNATIVES_COMPARISON.md
✅ env.example
✅ archive/ (for reference)
```

### **3. Verify Files to EXCLUDE**
```bash
# These should NOT be committed (sensitive):
❌ .env (contains your credentials)
❌ onedrive_token.pickle (contains your auth token)
❌ test_onedrive_token.pickle
```

## 🚀 **Deployment Steps**

### **Step 1: Commit to GitHub**
```bash
git add .
git commit -m "Add working OneDrive photo fetcher with reliable OAuth"
git push origin main
```

### **Step 2: Transfer to Production Machine**
```bash
# Copy sensitive files manually:
scp .env user@production-machine:/path/to/project/
scp onedrive_token.pickle user@production-machine:/path/to/project/
```

### **Step 3: Install on Production Machine**
```bash
# On production machine:
git clone <your-repo-url>
cd homeassistant-day-of-photos
pip install -r requirements.txt
```

### **Step 4: Configure Airflow**
```bash
# Copy DAG files:
cp onedrive_photos_fetcher.py /path/to/airflow/dags/
cp onedrive_photos_dag.py /path/to/airflow/dags/

# Set Airflow variables (in UI or CLI):
# ONEDRIVE_CLIENT_ID = your_client_id
# ONEDRIVE_CLIENT_SECRET = your_client_secret
```

### **Step 5: Test on Production**
```bash
# Test the setup:
python setup_onedrive.py
```

## 🔒 **Security Notes**

- ✅ Credentials in `.env` file (not in code)
- ✅ Token automatically managed
- ✅ No hardcoded secrets
- ✅ Sensitive files excluded from Git

## 📁 **File Structure After Deployment**

```
Production Machine:
├── onedrive_photos_fetcher.py    # From GitHub
├── onedrive_photos_dag.py        # From GitHub
├── setup_onedrive.py             # From GitHub
├── .env                          # Manually transferred
├── onedrive_token.pickle         # Manually transferred
└── requirements.txt               # From GitHub
```

## 🎯 **Success Criteria**

- ✅ Authentication works on production
- ✅ DAG loads in Airflow
- ✅ Variables set in Airflow
- ✅ DAG runs successfully
- ✅ Photos download to specified directory 