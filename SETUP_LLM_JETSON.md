# 🚀 Setting Up Local LLM on Jetson Orin AGX

This guide will help you install and configure a local LLM on your Jetson Orin AGX for intelligent photo analysis.

## 📋 Prerequisites

- Jetson Orin AGX with 64GB RAM
- Ubuntu 20.04 or later
- Python 3.8+
- At least 20GB free disk space

## 🎯 Recommended LLM Options

### Option 1: Ollama (Recommended)
**Pros**: Easy setup, good performance, supports vision models
**Cons**: Limited model selection

### Option 2: LM Studio
**Pros**: Wide model selection, good performance
**Cons**: More complex setup

### Option 3: Text Generation WebUI
**Pros**: Very flexible, supports many models
**Cons**: Resource intensive

## 🛠️ Installation Guide

### Step 1: Install Ollama (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Verify installation
ollama --version
```

### Step 2: Install a Vision-Capable Model

```bash
# Install Llama 3.2 (good for vision tasks)
ollama pull llama3.2

# Or install a smaller model for Jetson
ollama pull llama3.2:3b

# Test the model
ollama run llama3.2 "Hello, how are you?"
```

### Step 3: Install Python Dependencies

```bash
# Install required packages
pip3 install requests pillow opencv-python numpy

# For better performance
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Step 4: Test the LLM Integration

```bash
# Test if Ollama is accessible
curl http://localhost:11434/api/tags

# Test with a simple prompt
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "prompt": "Is this a good photo for a photo frame?",
    "stream": false
  }'
```

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_ENDPOINT=http://localhost:11434
LLM_TIMEOUT=30
```

### Model Selection

For Jetson Orin AGX, recommended models:

1. **llama3.2:3b** - Fast, good for basic tasks
2. **llama3.2:7b** - Better quality, moderate speed
3. **llama3.2** - Best quality, slower

## 🎯 Alternative: LM Studio Setup

If you prefer LM Studio:

```bash
# Download LM Studio
wget https://github.com/lmstudio-ai/lmstudio/releases/download/v0.2.0/LMStudio-0.2.0.AppImage

# Make executable
chmod +x LMStudio-0.2.0.AppImage

# Run LM Studio
./LMStudio-0.2.0.AppImage
```

Then:
1. Download a model (recommend: Llama 3.2 7B)
2. Start the local server
3. Update the LLM_PROVIDER in your `.env` file

## 🧪 Testing Your Setup

### Test 1: Basic LLM Functionality

```bash
python3 -c "
import requests
response = requests.post('http://localhost:11434/api/generate', 
  json={'model': 'llama3.2', 'prompt': 'Hello!', 'stream': False})
print(response.json()['response'])
"
```

### Test 2: Photo Analysis

```bash
# Test with a sample image
python3 onedrive_photos_script_enhanced.py --skip-transfer --filter-by-ai --ai-confidence 0.5
```

You should see output like:
```
✅ LLM detected and running
💬 LLM: GOOD: This appears to be a family photo with people smiling...
```

## 🔍 Troubleshooting

### Common Issues

1. **Ollama not starting**:
   ```bash
   sudo systemctl status ollama
   sudo journalctl -u ollama -f
   ```

2. **Model not found**:
   ```bash
   ollama list
   ollama pull llama3.2
   ```

3. **Memory issues**:
   - Use smaller models (3B instead of 7B)
   - Close other applications
   - Monitor memory usage: `htop`

4. **Slow performance**:
   - Use smaller models
   - Reduce batch size
   - Enable GPU acceleration if available

### Performance Optimization

```bash
# Monitor system resources
htop

# Check GPU usage
nvidia-smi

# Monitor Ollama logs
sudo journalctl -u ollama -f
```

## 🎯 Advanced Configuration

### Custom Prompts

You can customize the analysis prompts in `ai_image_analyzer_llm.py`:

```python
prompt = f"""Analyze this image for photo frame display suitability.

Consider:
- Personal value (family, friends, pets)
- Visual appeal (scenery, architecture, art)
- Technical quality (brightness, focus, composition)
- Inappropriate content (documents, screenshots, QR codes)

Respond: GOOD/BAD with brief explanation."""
```

### Model Fine-tuning

For better results, you can fine-tune the model on photo analysis:

```bash
# Create training data
# (This is advanced - contact for guidance)
```

## 📊 Expected Performance

On Jetson Orin AGX with 64GB RAM:

- **llama3.2:3b**: ~2-3 seconds per image
- **llama3.2:7b**: ~5-7 seconds per image
- **llama3.2**: ~10-15 seconds per image

## 🚀 Next Steps

1. **Test the setup** with a few sample images
2. **Adjust the confidence threshold** based on results
3. **Fine-tune prompts** for better accuracy
4. **Monitor performance** and optimize as needed

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u ollama -f`
2. Verify model installation: `ollama list`
3. Test basic functionality with curl commands
4. Check system resources: `htop`, `nvidia-smi`

The LLM analyzer will automatically fall back to rule-based analysis if the LLM is not available, so your system will continue to work even if there are LLM issues.
