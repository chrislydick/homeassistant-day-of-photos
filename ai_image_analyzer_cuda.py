#!/usr/bin/env python3
"""
CUDA-Accelerated AI Image Analyzer using PyTorch
Uses PyTorch CUDA operations for image processing on Jetson
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import cv2

# Try to import PyTorch with CUDA
try:
    import torch
    import torch.nn.functional as F
    from torchvision import transforms
    CUDA_AVAILABLE = torch.cuda.is_available()
    logger = logging.getLogger(__name__)
    if CUDA_AVAILABLE:
        logger.info("✅ PyTorch CUDA available")
    else:
        logger.warning("⚠️ PyTorch CUDA not available")
except ImportError:
    CUDA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ PyTorch not available")

class CUDAImageAnalyzer:
    """CUDA-accelerated image analyzer using PyTorch operations."""
    
    def __init__(self, device: str = "auto", quality_threshold: float = 0.6):
        """
        Initialize the CUDA image analyzer.
        
        Args:
            device: Device to use ('auto', 'cuda', 'cpu')
            quality_threshold: Quality score threshold for good/bad classification (0.0-1.0)
        """
        self.quality_threshold = quality_threshold
        self.device = self._setup_device(device)
        self.use_cuda = self.device == "cuda" and CUDA_AVAILABLE
        
        # Setup PyTorch transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        
        if self.use_cuda:
            logger.info("🚀 CUDA Image Analyzer initialized with PyTorch CUDA acceleration")
        else:
            logger.info("🚀 CUDA Image Analyzer initialized (CPU mode)")
    
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
        Analyze a single image for quality assessment using CUDA acceleration.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Calculate various quality metrics with CUDA acceleration
            blur_score = self._calculate_blur_score_cuda(image)
            brightness_score = self._calculate_brightness_score_cuda(image)
            contrast_score = self._calculate_contrast_score_cuda(image)
            edge_score = self._calculate_edge_score_cuda(image)
            saturation_score = self._calculate_saturation_score_cuda(image)
            
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
    
    def _calculate_blur_score_cuda(self, image: Image.Image) -> float:
        """Calculate image blur score using CUDA-accelerated operations."""
        try:
            # Convert to tensor and move to device
            img_tensor = self.transform(image).unsqueeze(0)
            if self.use_cuda:
                img_tensor = img_tensor.cuda()
            
            # Convert to grayscale
            gray = 0.299 * img_tensor[:, 0] + 0.587 * img_tensor[:, 1] + 0.114 * img_tensor[:, 2]
            
            # Apply Laplacian kernel for edge detection
            laplacian_kernel = torch.tensor([
                [0, 1, 0],
                [1, -4, 1],
                [0, 1, 0]
            ], dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            
            if self.use_cuda:
                laplacian_kernel = laplacian_kernel.cuda()
            
            # Apply convolution
            edges = F.conv2d(gray.unsqueeze(0), laplacian_kernel, padding=1)
            
            # Calculate variance (higher = less blurry)
            variance = torch.var(edges)
            blur_score = min(1.0, torch.log(variance + 1) / 10).item()
            
            return blur_score
            
        except Exception:
            return 0.5  # Default score if calculation fails
    
    def _calculate_brightness_score_cuda(self, image: Image.Image) -> float:
        """Calculate image brightness score using CUDA acceleration."""
        try:
            # Convert to tensor and move to device
            img_tensor = self.transform(image).unsqueeze(0)
            if self.use_cuda:
                img_tensor = img_tensor.cuda()
            
            # Convert to grayscale
            gray = 0.299 * img_tensor[:, 0] + 0.587 * img_tensor[:, 1] + 0.114 * img_tensor[:, 2]
            
            # Calculate mean brightness
            brightness = torch.mean(gray).item()
            
            return brightness
            
        except Exception:
            return 0.5
    
    def _calculate_contrast_score_cuda(self, image: Image.Image) -> float:
        """Calculate image contrast score using CUDA acceleration."""
        try:
            # Convert to tensor and move to device
            img_tensor = self.transform(image).unsqueeze(0)
            if self.use_cuda:
                img_tensor = img_tensor.cuda()
            
            # Convert to grayscale
            gray = 0.299 * img_tensor[:, 0] + 0.587 * img_tensor[:, 1] + 0.114 * img_tensor[:, 2]
            
            # Calculate standard deviation (contrast)
            contrast = torch.std(gray).item()
            
            # Normalize to 0-1 scale
            return min(1.0, contrast * 2)
            
        except Exception:
            return 0.5
    
    def _calculate_edge_score_cuda(self, image: Image.Image) -> float:
        """Calculate image edge density score using CUDA acceleration."""
        try:
            # Convert to tensor and move to device
            img_tensor = self.transform(image).unsqueeze(0)
            if self.use_cuda:
                img_tensor = img_tensor.cuda()
            
            # Convert to grayscale
            gray = 0.299 * img_tensor[:, 0] + 0.587 * img_tensor[:, 1] + 0.114 * img_tensor[:, 2]
            
            # Apply Sobel kernels for edge detection
            sobel_x = torch.tensor([
                [-1, 0, 1],
                [-2, 0, 2],
                [-1, 0, 1]
            ], dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            
            sobel_y = torch.tensor([
                [-1, -2, -1],
                [0, 0, 0],
                [1, 2, 1]
            ], dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            
            if self.use_cuda:
                sobel_x = sobel_x.cuda()
                sobel_y = sobel_y.cuda()
            
            # Apply convolutions
            edges_x = F.conv2d(gray.unsqueeze(0), sobel_x, padding=1)
            edges_y = F.conv2d(gray.unsqueeze(0), sobel_y, padding=1)
            
            # Calculate edge magnitude
            edges = torch.sqrt(edges_x**2 + edges_y**2)
            
            # Calculate edge density
            edge_density = torch.mean(edges > 0.1).item()
            
            # Normalize to 0-1 scale
            return min(1.0, edge_density * 10)
            
        except Exception:
            return 0.5
    
    def _calculate_saturation_score_cuda(self, image: Image.Image) -> float:
        """Calculate image saturation score using CUDA acceleration."""
        try:
            # Convert to tensor and move to device
            img_tensor = self.transform(image).unsqueeze(0)
            if self.use_cuda:
                img_tensor = img_tensor.cuda()
            
            # Calculate saturation using HSV-like approach
            r, g, b = img_tensor[:, 0], img_tensor[:, 1], img_tensor[:, 2]
            
            # Calculate max and min values
            max_val = torch.max(torch.max(r, g), b)
            min_val = torch.min(torch.min(r, g), b)
            
            # Calculate saturation
            saturation = (max_val - min_val) / (max_val + 1e-8)
            sat_score = torch.mean(saturation).item()
            
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
        Analyze multiple images in batch using CUDA acceleration.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary with 'good' and 'bad' image lists
        """
        logger.info(f"🔍 Analyzing {len(image_paths)} images with {'CUDA' if self.use_cuda else 'CPU'} acceleration...")
        
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
        """Clean up CUDA resources."""
        if self.use_cuda and torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("🧹 CUDA Image Analyzer resources cleaned up")


def create_analyzer(device: str = "auto", confidence_threshold: float = 0.7):
    """Factory function to create a CUDA image analyzer."""
    return CUDAImageAnalyzer(device=device, quality_threshold=confidence_threshold)
