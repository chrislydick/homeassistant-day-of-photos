# 🚀 Quick Start: AI Image Analysis

Get AI-powered image quality analysis running in 5 minutes!

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
pip3 install -r requirements_standalone.txt
```

### 2. Test AI Analyzer
```bash
python3 test_ai_analyzer.py
```

### 3. Update Your Crontab
```bash
./setup_crontab_enhanced.sh
```

## 🎯 What This Gives You

- **Automatic filtering** of screenshots, documents, blurry images
- **Quality scoring** for all your photos
- **Smart categorization** (people, pets, scenery, etc.)
- **Only good images** transferred to Home Assistant
- **Bad images** moved to `bad_images/` folder for review

## 🔧 Your New Crontab

Your crontab will now run at 3:00 AM daily with:
```bash
00 03 * * * cd /home/chrislydick/git/homeassistant-day-of-photos && python3 onedrive_photos_script_enhanced.py --ai-device auto --ai-confidence 0.7 --filter-by-ai --move-bad-images >> /home/chrislydick/git/homeassistant-day-of-photos/cron.log 2>&1
```

## 🧪 Test It Now

```bash
# Test with today's photos (no transfer)
python3 onedrive_photos_script_enhanced.py --skip-transfer --filter-by-ai

# Check results
ls -la images/
ls -la images/bad_images/  # if any bad images found
```

## 📊 Expected Results

- **Good images**: People, pets, scenery, architecture
- **Bad images**: Screenshots, documents, whiteboards, blurry photos
- **Quality scores**: 0.0-1.0 (higher = better)
- **Processing speed**: ~2-5 seconds per image on your Jetson Orin

## 🆘 Need Help?

- **Full documentation**: `README_AI_FEATURES.md`
- **Test script**: `python3 test_ai_analyzer.py`
- **Help**: `python3 onedrive_photos_script_enhanced.py --help`

## 🎉 You're Done!

Your system will now automatically:
1. Download photos from OneDrive
2. Analyze them with AI
3. Keep only the good ones
4. Transfer to Home Assistant
5. Log everything for review

The AI runs on your Jetson Orin's GPU for maximum performance! 🚀
