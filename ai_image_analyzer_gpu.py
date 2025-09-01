#!/usr/bin/env python3
"""
GPU-Accelerated AI Image Analyzer for Photo Quality Assessment
Uses CUDA for image processing operations to leverage Jetson GPU
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import cv2

# Try to import CUDA-accelerated OpenCV
try:
    import cv2.cuda as cv2_cuda
    # Test if CUDA actually works
    test_gpu = cv2_cuda.GpuMat()
    test_gpu.upload(np.zeros((10, 10), dtype=np.uint8))
    CUDA_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ CUDA-accelerated OpenCV available")
except Exception:
    CUDA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ CUDA-accelerated OpenCV not available, falling back to CPU")

class GPUImageAnalyzer:
    """GPU-accelerated image analyzer using CUDA operations."""
    
    def __init__(self, device: str = "auto", quality_threshold: float = 0.6):
        """
        Initialize the GPU image analyzer.
        
        Args:
            device: Device to use ('auto', 'cuda', 'cpu')
            quality_threshold: Quality score threshold for good/bad classification (0.0-1.0)
        """
        self.quality_threshold = quality_threshold
        self.device = self._setup_device(device)
        self.use_cuda = self.device == "cuda" and CUDA_AVAILABLE
        
        if self.use_cuda:
            logger.info("🚀 GPU Image Analyzer initialized with CUDA acceleration")
        else:
            logger.info("🚀 GPU Image Analyzer initialized (CPU mode)")
    
    def _setup_device(self, device: str) -> str:
        """Setup the best available device."""
        if device == "auto":
            if CUDA_AVAILABLE:
                device = "cuda"
                logger.info("✅ CUDA available, using GPU acceleration")
            else:
                device = "cpu"
                logger.info("ℹ️ CUDA not available, using CPU")
        elif device == "cuda" and not CUDA_AVAILABLE:
            logger.warning("⚠️ CUDA requested but not available, falling back to CPU")
            device = "cpu"
        return device
    
    def analyze_image(self, image_path: Path) -> Dict[str, any]:
        """
        Analyze a single image for quality assessment using GPU acceleration.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Calculate various quality metrics with GPU acceleration
            blur_score = self._calculate_blur_score_gpu(image)
            brightness_score = self._calculate_brightness_score_gpu(image)
            contrast_score = self._calculate_contrast_score_gpu(image)
            edge_score = self._calculate_edge_score_gpu(image)
            saturation_score = self._calculate_saturation_score_gpu(image)
            
            # Calculate overall quality score
            quality_score = self._calculate_overall_score(
                blur_score, brightness_score, contrast_score, 
                edge_score, saturation_score
            )
            
            # Determine if image is good or bad based on quality threshold
            is_good_image = quality_score >= self.quality_threshold
            
            # Categorize image based on visual characteristics
            category = self._categorize_image(
                blur_score, brightness_score, contrast_score, 
                edge_score, saturation_score
            )
            
            return {
                'path': str(image_path),
                'is_good': is_good_image,
                'quality_score': quality_score,
                'category': category,
                'analysis': {
                    'blur_score': blur_score,
                    'brightness_score': brightness_score,
                    'contrast_score': contrast_score,
                    'edge_score': edge_score,
                    'saturation_score': saturation_score
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze {image_path}: {e}")
            return {
                'path': str(image_path),
                'is_good': False,
                'error': str(e)
            }
    
    def _calculate_blur_score_gpu(self, image: Image.Image) -> float:
        """Calculate image blur score using GPU-accelerated Laplacian variance."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            if self.use_cuda:
                # Upload to GPU
                gpu_image = cv2_cuda.GpuMat()
                gpu_image.upload(cv_image)
                
                # Convert to grayscale on GPU
                gpu_gray = cv2_cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
                
                # Download for CPU processing (Laplacian not available on GPU)
                gray = gpu_gray.download()
            else:
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (higher = less blurry)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 scale (log scale for better distribution)
            blur_score = min(1.0, np.log(laplacian_var + 1) / 10)
            return blur_score
            
        except Exception:
            return 0.5  # Default score if calculation fails
    
    def _calculate_brightness_score_gpu(self, image: Image.Image) -> float:
        """Calculate image brightness score using GPU acceleration."""
        try:
            if self.use_cuda:
                # Convert PIL image to OpenCV format
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Upload to GPU
                gpu_image = cv2_cuda.GpuMat()
                gpu_image.upload(cv_image)
                
                # Convert to grayscale on GPU
                gpu_gray = cv2_cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
                
                # Calculate mean on GPU
                mean_val = cv2_cuda.mean(gpu_gray)[0]
                brightness = mean_val / 255.0
            else:
                # CPU fallback
                gray = image.convert('L')
                brightness = np.mean(np.array(gray)) / 255.0
            
            return brightness
            
        except Exception:
            return 0.5
    
    def _calculate_contrast_score_gpu(self, image: Image.Image) -> float:
        """Calculate image contrast score using GPU acceleration."""
        try:
            if self.use_cuda:
                # Convert PIL image to OpenCV format
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Upload to GPU
                gpu_image = cv2_cuda.GpuMat()
                gpu_image.upload(cv_image)
                
                # Convert to grayscale on GPU
                gpu_gray = cv2_cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
                
                # Download for CPU processing (std calculation)
                gray = gpu_gray.download()
            else:
                gray = image.convert('L')
                gray = np.array(gray)
            
            # Calculate standard deviation
            contrast = np.std(gray) / 255.0
            
            # Normalize to 0-1 scale
            return min(1.0, contrast * 2)
            
        except Exception:
            return 0.5
    
    def _calculate_edge_score_gpu(self, image: Image.Image) -> float:
        """Calculate image edge density score using GPU acceleration."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            if self.use_cuda:
                # Upload to GPU
                gpu_image = cv2_cuda.GpuMat()
                gpu_image.upload(cv_image)
                
                # Convert to grayscale on GPU
                gpu_gray = cv2_cuda.cvtColor(gpu_image, cv2.COLOR_BGR2GRAY)
                
                # Download for CPU processing (Canny not available on GPU)
                gray = gpu_gray.download()
            else:
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate edge density
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Normalize to 0-1 scale
            return min(1.0, edge_density * 100)
            
        except Exception:
            return 0.5
    
    def _calculate_saturation_score_gpu(self, image: Image.Image) -> float:
        """Calculate image saturation score using GPU acceleration."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            if self.use_cuda:
                # Upload to GPU
                gpu_image = cv2_cuda.GpuMat()
                gpu_image.upload(cv_image)
                
                # Convert to HSV on GPU
                gpu_hsv = cv2_cuda.cvtColor(gpu_image, cv2.COLOR_BGR2HSV)
                
                # Extract saturation channel on GPU
                gpu_saturation = cv2_cuda.split(gpu_hsv)[1]
                
                # Calculate mean on GPU
                mean_val = cv2_cuda.mean(gpu_saturation)[0]
                sat_score = mean_val / 255.0
            else:
                # CPU fallback
                hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                saturation = hsv[:, :, 1]
                sat_score = np.mean(saturation) / 255.0
            
            return sat_score
            
        except Exception:
            return 0.5
    
    def _calculate_overall_score(self, blur_score: float, brightness_score: float, 
                                contrast_score: float, edge_score: float, 
                                saturation_score: float) -> float:
        """Calculate overall quality score from individual metrics."""
        # Weighted combination of scores
        weights = {
            'blur': 0.3,      # Blur is most important
            'brightness': 0.2, # Brightness matters
            'contrast': 0.2,   # Contrast is important
            'edge': 0.2,       # Edge detection helps
            'saturation': 0.1  # Saturation is least important
        }
        
        overall_score = (
            blur_score * weights['blur'] +
            brightness_score * weights['brightness'] +
            contrast_score * weights['contrast'] +
            edge_score * weights['edge'] +
            saturation_score * weights['saturation']
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def _categorize_image(self, blur_score: float, brightness_score: float, 
                          contrast_score: float, edge_score: float, 
                          saturation_score: float) -> str:
        """Categorize the type of image based on characteristics."""
        # High edge density suggests text/documents
        if edge_score > 0.7 and contrast_score > 0.6:
            return 'document'
        
        # Low saturation suggests screenshots
        if saturation_score < 0.3 and brightness_score > 0.6:
            return 'screenshot'
        
        # Very blurry images
        if blur_score < 0.2:
            return 'blurry'
        
        # Good quality images
        if blur_score > 0.6 and contrast_score > 0.5:
            return 'good_quality'
        
        # Low contrast images
        if contrast_score < 0.3:
            return 'low_contrast'
        
        return 'other'
    
    def analyze_batch(self, image_paths: List[Path]) -> Dict[str, List]:
        """
        Analyze multiple images in batch using GPU acceleration.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary with 'good' and 'bad' image lists
        """
        logger.info(f"🔍 Analyzing {len(image_paths)} images with {'GPU' if self.use_cuda else 'CPU'} acceleration...")
        
        good_images = []
        bad_images = []
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"📸 Analyzing image {i+1}/{len(image_paths)}: {image_path.name}")
            
            result = self.analyze_image(image_path)
            
            if result.get('is_good', False):
                good_images.append(result)
                logger.info(f"✅ Good image: {image_path.name} (score: {result.get('quality_score', 0):.2f})")
            else:
                bad_images.append(result)
                logger.warning(f"❌ Bad image: {image_path.name} (score: {result.get('quality_score', 0):.2f})")
        
        logger.info(f"🎯 Analysis complete: {len(good_images)} good, {len(bad_images)} bad images")
        
        return {
            'good': good_images,
            'bad': bad_images,
            'total': len(image_paths)
        }
    
    def cleanup(self):
        """Clean up GPU resources."""
        if self.use_cuda:
            try:
                cv2_cuda.resetDevice()
            except Exception:
                pass  # Ignore cleanup errors
        logger.info("🧹 GPU Image Analyzer resources cleaned up")


def create_analyzer(device: str = "auto", confidence_threshold: float = 0.7):
    """Factory function to create a GPU image analyzer."""
    return GPUImageAnalyzer(device=device, quality_threshold=confidence_threshold)
