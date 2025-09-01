# 🚀 GPU-Optimized LLM Setup for Jetson Orin AGX

This guide will help you install and configure a local LLM to run on your Jetson Orin AGX GPU for maximum performance.

## 📋 Prerequisites

- Jetson Orin AGX with 64GB RAM
- Ubuntu 20.04 or later
- Python 3.8+
- At least 20GB free disk space
- CUDA 11.4+ (should be pre-installed)

## 🎯 GPU-Optimized LLM Options

### Option 1: Ollama with GPU Support (Recommended)
**Pros**: Easy setup, excellent GPU utilization, supports vision models
**Cons**: Limited model selection

### Option 2: LM Studio with GPU
**Pros**: Wide model selection, good GPU performance
**Cons**: More complex setup

### Option 3: Text Generation WebUI with GPU
**Pros**: Very flexible, supports many models, excellent GPU utilization
**Cons**: Resource intensive

## 🛠️ Installation Guide

### Step 1: Verify GPU Setup

```bash
# Check GPU availability
nvidia-smi

# Check CUDA version
nvcc --version

# Check GPU memory
nvidia-smi --query-gpu=memory.total --format=csv
```

### Step 2: Install Ollama with GPU Support

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Verify installation
ollama --version

# Check if GPU is detected
ollama list
```

### Step 3: Install GPU-Optimized Models

```bash
# Install Llama 3.2 with GPU support
ollama pull llama3.2:3b

# For better quality (uses more GPU memory)
ollama pull llama3.2:7b

# Test GPU utilization
ollama run llama3.2:3b "Hello, how are you?"
nvidia-smi  # Check GPU usage
```

### Step 4: Install Python Dependencies with GPU Support

```bash
# Install PyTorch with CUDA support
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip3 install requests pillow opencv-python numpy

# Verify GPU support
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"
```

### Step 5: Configure GPU Memory Allocation

Create a GPU configuration file:

```bash
# Create Ollama config directory
mkdir -p ~/.ollama

# Create GPU configuration
cat > ~/.ollama/config.json << EOF
{
  "gpu_layers": 50,
  "numa": false,
  "gpu_memory_utilization": 0.8
}
EOF
```

## 🔧 GPU Optimization

### Memory Management

```bash
# Monitor GPU memory usage
watch -n 1 nvidia-smi

# Set GPU memory limits for Ollama
export OLLAMA_GPU_LAYERS=50
export OLLAMA_GPU_MEMORY_UTILIZATION=0.8
```

### Performance Tuning

```bash
# Optimize for Jetson Orin
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=1

# Set optimal thread count
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
```

## 🎯 Model Selection for Jetson Orin AGX

### Recommended Models (GPU Optimized)

1. **llama3.2:3b** - Fast, good for basic tasks, ~2-3GB GPU memory
2. **llama3.2:7b** - Better quality, moderate speed, ~4-6GB GPU memory
3. **llama3.2:8b** - Best quality, slower, ~6-8GB GPU memory

### Install Vision-Capable Models

```bash
# Install models that support image analysis
ollama pull llama3.2:3b
ollama pull llama3.2:7b

# Test vision capabilities
ollama run llama3.2:3b "Describe this image: [base64_image_data]"
```

## 🧪 Testing GPU Performance

### Test 1: Basic GPU Functionality

```bash
# Test GPU detection
python3 -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU count: {torch.cuda.device_count()}')
print(f'GPU name: {torch.cuda.get_device_name(0)}')
print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
"
```

### Test 2: Ollama GPU Performance

```bash
# Test Ollama with GPU
time ollama run llama3.2:3b "Generate a 100-word story about a photo frame"

# Monitor GPU usage during test
nvidia-smi -l 1
```

### Test 3: Photo Analysis with GPU

```bash
# Test the photo analysis system
python3 onedrive_photos_script_enhanced.py --skip-transfer --filter-by-ai --ai-confidence 0.5
```

## 🔍 Troubleshooting GPU Issues

### Common GPU Problems

1. **GPU not detected**:
   ```bash
   nvidia-smi
   sudo systemctl restart ollama
   ```

2. **Out of GPU memory**:
   ```bash
   # Use smaller model
   ollama pull llama3.2:3b
   
   # Reduce GPU layers
   export OLLAMA_GPU_LAYERS=25
   ```

3. **Slow performance**:
   ```bash
   # Check GPU utilization
   nvidia-smi -l 1
   
   # Optimize memory allocation
   export OLLAMA_GPU_MEMORY_UTILIZATION=0.9
   ```

### Performance Monitoring

```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# Detailed GPU stats
nvidia-smi --query-gpu=timestamp,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv -l 1
```

## 🎯 Advanced GPU Configuration

### Custom Ollama Configuration

```bash
# Create advanced config
cat > ~/.ollama/config.json << EOF
{
  "gpu_layers": 50,
  "numa": false,
  "gpu_memory_utilization": 0.8,
  "context_length": 4096,
  "batch_size": 512,
  "threads": 8
}
EOF
```

### Environment Variables

Add to your `.env` file:

```bash
# GPU Configuration
CUDA_VISIBLE_DEVICES=0
OLLAMA_GPU_LAYERS=50
OLLAMA_GPU_MEMORY_UTILIZATION=0.8
OMP_NUM_THREADS=8
MKL_NUM_THREADS=8

# LLM Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:3b
LLM_ENDPOINT=http://localhost:11434
LLM_TIMEOUT=30
LLM_USE_GPU=true
```

## 📊 Expected Performance on Jetson Orin AGX

With GPU acceleration:

- **llama3.2:3b**: ~1-2 seconds per image
- **llama3.2:7b**: ~3-5 seconds per image
- **llama3.2:8b**: ~5-8 seconds per image

### GPU Memory Usage

- **llama3.2:3b**: ~2-3GB GPU memory
- **llama3.2:7b**: ~4-6GB GPU memory
- **llama3.2:8b**: ~6-8GB GPU memory

## 🚀 Next Steps

1. **Install Ollama** with GPU support
2. **Download a vision-capable model**
3. **Test GPU performance**
4. **Configure the LLM analyzer** to use GPU
5. **Monitor and optimize** performance

## 📞 Support

If you encounter GPU issues:

1. Check GPU status: `nvidia-smi`
2. Verify CUDA installation: `nvcc --version`
3. Test Ollama GPU detection: `ollama list`
4. Monitor GPU usage during operation
5. Check system logs: `sudo journalctl -u ollama -f`

The LLM analyzer will automatically detect GPU availability and optimize performance accordingly.
