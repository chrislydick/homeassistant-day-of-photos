# AI-Powered Image Quality Analysis

This repository now includes AI-powered image quality assessment to automatically filter out low-quality images before transferring them to Home Assistant.

## 🚀 Features

### AI Image Analysis
- **Automatic Quality Assessment**: Uses pre-trained ResNet50 model to classify images
- **Smart Filtering**: Identifies and filters out:
  - Screenshots and computer monitors
  - Documents and text-heavy images
  - Whiteboards and chalkboards
  - Blurry or low-quality photos
- **Quality Scoring**: Provides numerical quality scores (0.0-1.0)
- **Image Categorization**: Automatically categorizes images as people, pets, scenery, architecture, etc.

### Technical Analysis
- **Blur Detection**: Uses Laplacian variance to detect blurry images
- **Brightness Analysis**: Evaluates image brightness levels
- **Contrast Assessment**: Measures image contrast quality

## 🛠️ Installation

### 1. Install Dependencies
```bash
pip3 install -r requirements_standalone.txt
```

### 2. Verify Installation
```bash
python3 test_ai_analyzer.py
```

## 📖 Usage

### Basic AI Analysis
```bash
# Run with AI analysis enabled (default)
python3 onedrive_photos_script_enhanced.py

# Skip AI analysis
python3 onedrive_photos_script_enhanced.py --skip-ai-analysis
```

### Advanced AI Options
```bash
# Custom confidence threshold (0.0-1.0)
python3 onedrive_photos_script_enhanced.py --ai-confidence 0.8

# Force CPU usage (if GPU issues)
python3 onedrive_photos_script_enhanced.py --ai-device cpu

# Only transfer AI-approved "good" images
python3 onedrive_photos_script_enhanced.py --filter-by-ai

# Move bad images to separate folder
python3 onedrive_photos_script_enhanced.py --move-bad-images

# Combine multiple options
python3 onedrive_photos_script_enhanced.py \
    --ai-confidence 0.75 \
    --filter-by-ai \
    --move-bad-images \
    --ai-device auto
```

### Crontab Setup with AI
```bash
# Make the setup script executable
chmod +x setup_crontab_enhanced.sh

# Run the enhanced setup
./setup_crontab_enhanced.sh
```

## 🎯 How It Works

### 1. Image Download
- Downloads photos from OneDrive for the target date
- Supports multiple image formats (JPG, PNG, BMP, TIFF)

### 2. AI Analysis
- Loads pre-trained ResNet50 model
- Analyzes each image for:
  - Object/content classification
  - Quality scoring
  - Technical characteristics (blur, brightness, contrast)

### 3. Quality Classification
- **Good Images**: People, pets, scenery, architecture, action shots
- **Bad Images**: Screenshots, documents, whiteboards, blurry photos

### 4. Transfer & Cleanup
- Transfers only good images to Home Assistant (if `--filter-by-ai` enabled)
- Moves bad images to `bad_images/` folder (if `--move-bad-images` enabled)
- Cleans up temporary files

## 🔧 Configuration

### Environment Variables
```bash
# AI Analysis Settings
AI_DEVICE=auto              # auto, cuda, cpu
AI_CONFIDENCE=0.7           # 0.0-1.0
FILTER_BY_AI=true           # true/false
MOVE_BAD_IMAGES=true        # true/false
```

### Command Line Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--skip-ai-analysis` | Skip AI analysis | False |
| `--ai-device` | Device for AI (auto/cuda/cpu) | auto |
| `--ai-confidence` | Confidence threshold | 0.7 |
| `--filter-by-ai` | Only transfer good images | False |
| `--move-bad-images` | Move bad images to folder | False |

## 🧪 Testing

### Test AI Analyzer
```bash
# Test basic functionality
python3 test_ai_analyzer.py

# Test with specific image
python3 -c "
from ai_image_analyzer import create_analyzer
analyzer = create_analyzer()
result = analyzer.analyze_image('path/to/image.jpg')
print(f'Quality Score: {result[\"quality_score\"]:.3f}')
analyzer.cleanup()
"
```

### Test Full Pipeline
```bash
# Test download and AI analysis without transfer
python3 onedrive_photos_script_enhanced.py \
    --skip-transfer \
    --filter-by-ai \
    --move-bad-images
```

## 📊 Performance

### Jetson Orin 64G Performance
- **GPU Mode**: ~2-5 seconds per image
- **CPU Mode**: ~5-15 seconds per image
- **Memory Usage**: ~2-4GB during analysis
- **Model Loading**: ~10-15 seconds initial load

### Optimization Tips
1. **Use GPU**: Ensure `--ai-device auto` or `--ai-device cuda`
2. **Batch Processing**: Process multiple images together for efficiency
3. **Confidence Tuning**: Adjust `--ai-confidence` based on your needs
4. **Memory Management**: Script automatically cleans up GPU memory

## 🐛 Troubleshooting

### Common Issues

#### CUDA Out of Memory
```bash
# Force CPU usage
python3 onedrive_photos_script_enhanced.py --ai-device cpu
```

#### Model Download Issues
```bash
# Clear torch cache
python3 -c "import torch; torch.hub.clear_cache()"

# Manual model download
python3 -c "import torchvision; torchvision.models.resnet50(weights='IMAGENET1K_V2')"
```

#### Import Errors
```bash
# Reinstall dependencies
pip3 uninstall torch torchvision opencv-python
pip3 install -r requirements_standalone.txt
```

### Debug Mode
```bash
# Enable verbose logging
export PYTHONPATH=.
python3 -u onedrive_photos_script_enhanced.py --skip-transfer 2>&1 | tee debug.log
```

## 🔮 Future Enhancements

### Planned Features
- **Custom Model Training**: Train on your specific photo collection
- **Face Recognition**: Identify family members and friends
- **Scene Classification**: Better categorization of photo types
- **Batch Optimization**: Parallel processing for multiple images
- **Model Quantization**: Reduced memory usage and faster inference

### DeepStream Integration
For even better performance on Jetson, consider upgrading to NVIDIA DeepStream:
- **Performance**: 5-10x faster than current implementation
- **Memory**: 2-3x less memory usage
- **Optimization**: NVIDIA-optimized inference pipeline

## 📝 Logging

### AI Analysis Logs
```
🤖 Starting AI-powered image quality analysis...
📸 Analyzing image 1/15: IMG_20231201_120000.jpg
✅ Good image: IMG_20231201_120000.jpg (score: 0.85)
📸 Analyzing image 2/15: IMG_20231201_120100.jpg
❌ Bad image: IMG_20231201_120100.jpg (score: 0.32)
🎯 Analysis complete: 12 good, 3 bad images
```

### Quality Scores Explained
- **0.9-1.0**: Excellent quality photos
- **0.7-0.9**: Good quality photos
- **0.5-0.7**: Acceptable quality photos
- **0.3-0.5**: Poor quality photos
- **0.0-0.3**: Very poor quality photos

## 🤝 Contributing

### Adding New Image Categories
Edit `ai_image_analyzer.py` to add new desirable/undesirable keywords:

```python
desirable_keywords = [
    'person', 'people', 'human', 'face', 'portrait', 'family',
    'pet', 'dog', 'cat', 'animal', 'wildlife',
    'landscape', 'nature', 'scenery', 'mountain', 'beach', 'forest',
    'building', 'architecture', 'city', 'street',
    'your_new_category'  # Add here
]
```

### Custom Quality Metrics
Implement new quality assessment methods in the `AIImageAnalyzer` class:

```python
def _calculate_custom_score(self, image: Image.Image) -> float:
    """Calculate custom quality metric."""
    # Your implementation here
    pass
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PyTorch**: Deep learning framework
- **TorchVision**: Pre-trained models and transforms
- **OpenCV**: Computer vision library
- **NVIDIA Jetson**: Hardware platform optimization
