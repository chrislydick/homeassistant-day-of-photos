#!/usr/bin/env python3
"""
Simplified AI Image Analyzer for Photo Quality Assessment
Works with system PyTorch without requiring torchvision
Uses basic image processing and heuristics for quality assessment
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

class SimpleImageAnalyzer:
    """Simplified image analyzer using basic computer vision techniques."""
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the simplified image analyzer.
        
        Args:
            confidence_threshold: Minimum quality score threshold
        """
        self.confidence_threshold = confidence_threshold
        logger.info("🚀 Simple Image Analyzer initialized")
    
    def analyze_image(self, image_path: Path) -> Dict[str, any]:
        """
        Analyze a single image for quality assessment.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Calculate various quality metrics
            blur_score = self._calculate_blur_score(image)
            brightness_score = self._calculate_brightness_score(image)
            contrast_score = self._calculate_contrast_score(image)
            edge_score = self._calculate_edge_score(image)
            saturation_score = self._calculate_saturation_score(image)
            
            # Calculate overall quality score
            quality_score = self._calculate_overall_score(
                blur_score, brightness_score, contrast_score, 
                edge_score, saturation_score
            )
            
            # Determine if image is good or bad
            is_good_image = self._classify_image_quality(
                quality_score, blur_score, brightness_score, contrast_score
            )
            
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
    
    def _calculate_blur_score(self, image: Image.Image) -> float:
        """Calculate image blur score using Laplacian variance."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (higher = less blurry)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 scale (log scale for better distribution)
            blur_score = min(1.0, np.log(laplacian_var + 1) / 10)
            return blur_score
            
        except Exception:
            return 0.5  # Default score if calculation fails
    
    def _calculate_brightness_score(self, image: Image.Image) -> float:
        """Calculate image brightness score."""
        try:
            # Convert to grayscale and calculate mean brightness
            gray = image.convert('L')
            brightness = np.mean(np.array(gray)) / 255.0
            
            # Normalize to 0-1 scale
            return brightness
            
        except Exception:
            return 0.5
    
    def _calculate_contrast_score(self, image: Image.Image) -> float:
        """Calculate image contrast score."""
        try:
            # Convert to grayscale and calculate standard deviation
            gray = image.convert('L')
            contrast = np.std(np.array(gray)) / 255.0
            
            # Normalize to 0-1 scale
            return min(1.0, contrast * 2)
            
        except Exception:
            return 0.5
    
    def _calculate_edge_score(self, image: Image.Image) -> float:
        """Calculate image edge density score."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate edge density
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Normalize to 0-1 scale
            return min(1.0, edge_density * 100)
            
        except Exception:
            return 0.5
    
    def _calculate_saturation_score(self, image: Image.Image) -> float:
        """Calculate image saturation score."""
        try:
            # Convert to HSV color space
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Extract saturation channel
            saturation = hsv[:, :, 1]
            
            # Calculate mean saturation
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
    
    def _classify_image_quality(self, quality_score: float, blur_score: float, 
                               brightness_score: float, contrast_score: float) -> bool:
        """Classify whether an image is good or bad."""
        # Check individual thresholds (more lenient)
        if blur_score < 0.15:  # Very blurry (lowered from 0.3)
            return False
        if brightness_score < 0.05 or brightness_score > 0.95:  # Very dark or very bright (widened from 0.1-0.9)
            return False
        if contrast_score < 0.1:  # Very low contrast (lowered from 0.2)
            return False
        
        # Use overall quality score (this is what --ai-confidence controls)
        return quality_score >= self.confidence_threshold
    
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
        Analyze multiple images in batch.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary with 'good' and 'bad' image lists
        """
        logger.info(f"🔍 Analyzing {len(image_paths)} images...")
        
        good_images = []
        bad_images = []
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"📸 Analyzing image {i+1}/{len(image_paths)}: {image_path.name}")
            
            result = self.analyze_image(image_path)
            
            if result.get('is_good', False):
                good_images.append(result)
                logger.info(f"✅ GOOD image: {image_path.name} (score: {result.get('quality_score', 0):.2f})")
            else:
                bad_images.append(result)
                logger.info(f"❌ BAD image: {image_path.name} (score: {result.get('quality_score', 0):.2f})")
        
        logger.info(f"🎯 Analysis complete: {len(good_images)} good, {len(bad_images)} bad images")
        
        return {
            'good': good_images,
            'bad': bad_images,
            'total': len(image_paths)
        }
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("🧹 Simple Image Analyzer resources cleaned up")


def create_analyzer(device: str = "auto", confidence_threshold: float = 0.7):
    """Factory function to create a simple image analyzer."""
    # Ignore device parameter for simple analyzer
    return SimpleImageAnalyzer(confidence_threshold=confidence_threshold)
