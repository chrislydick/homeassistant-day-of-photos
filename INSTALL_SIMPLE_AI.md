# 🚀 Quick Install: Simplified AI Image Analysis

Get AI-powered image quality analysis running in 2 minutes on your Jetson Orin!

## ⚡ Super Quick Setup

### 1. Install Dependencies
```bash
pip3 install opencv-python numpy
```

### 2. Test It
```bash
python3 test_simple_analyzer.py
```

### 3. Update Your Crontab
```bash
./setup_crontab_enhanced.sh
```

## 🎯 What You Get

- **Automatic filtering** of blurry, low-contrast, and poor quality images
- **Quality scoring** based on blur, brightness, contrast, edges, and saturation
- **Smart categorization** (documents, screenshots, blurry, good quality, etc.)
- **Only good images** transferred to Home Assistant
- **Bad images** moved to `bad_images/` folder for review

## 🔧 How It Works

The simplified analyzer uses **computer vision techniques** instead of deep learning:

- **Blur Detection**: Laplacian variance analysis
- **Brightness Analysis**: Histogram analysis
- **Contrast Assessment**: Standard deviation of pixel values
- **Edge Detection**: Canny edge detection for document identification
- **Saturation Analysis**: HSV color space analysis

## 📊 Performance

- **Speed**: ~0.5-2 seconds per image (much faster than deep learning)
- **Memory**: ~100-200MB (very lightweight)
- **Accuracy**: Good for basic quality assessment
- **No GPU Required**: Works on CPU or GPU

## 🧪 Test It Now

```bash
# Test the analyzer
python3 test_simple_analyzer.py

# Test with your script (no transfer)
python3 onedrive_photos_script_enhanced.py --skip-transfer --filter-by-ai

# Check results
ls -la images/
ls -la images/bad_images/  # if any bad images found
```

## 🔄 Your New Crontab

```bash
00 03 * * * cd /home/chrislydick/git/homeassistant-day-of-photos && python3 onedrive_photos_script_enhanced.py --ai-confidence 0.6 --filter-by-ai --move-bad-images >> /home/chrislydick/git/homeassistant-day-of-photos/cron.log 2>&1
```

## 🎛️ Tune the Settings

### Confidence Threshold
- **0.5**: More lenient (keeps more images)
- **0.6**: Balanced (recommended)
- **0.7**: Stricter (higher quality only)

### What Gets Filtered Out
- **Blurry images** (blur_score < 0.3)
- **Too dark/bright** (brightness < 0.1 or > 0.9)
- **Low contrast** (contrast < 0.2)
- **Documents** (high edge density)
- **Screenshots** (low saturation + high brightness)

## 🆘 Troubleshooting

### OpenCV Issues
```bash
# Reinstall OpenCV
pip3 uninstall opencv-python
pip3 install opencv-python
```

### Permission Issues
```bash
# Use user installation
pip3 install opencv-python --user
```

### Test Individual Components
```bash
# Test OpenCV
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"

# Test PIL
python3 -c "from PIL import Image; print('PIL available')"

# Test numpy
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"
```

## 🎉 You're Done!

Your system will now automatically:
1. Download photos from OneDrive
2. Analyze them with computer vision
3. Keep only the good ones
4. Transfer to Home Assistant
5. Log everything for review

**No deep learning models needed!** 🚀

## 🔮 Want More Advanced AI?

If you want the full deep learning experience later:
```bash
# Install PyTorch with CUDA support
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# The script will automatically use the full AI analyzer
```
