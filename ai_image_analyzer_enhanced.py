#!/usr/bin/env python3
"""
Enhanced AI Image Analyzer for Photo Quality Assessment
Uses advanced computer vision techniques for robust image quality analysis
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

class EnhancedImageAnalyzer:
    """Enhanced image analyzer using advanced computer vision techniques."""
    
    def __init__(self, device: str = "auto", quality_threshold: float = 0.6):
        """
        Initialize the enhanced image analyzer.
        
        Args:
            device: Device to use ('auto', 'cuda', 'cpu') - kept for compatibility
            quality_threshold: Quality score threshold for good/bad classification (0.0-1.0)
        """
        self.quality_threshold = quality_threshold
        logger.info("🚀 Enhanced AI Image Analyzer initialized with advanced computer vision")
    
    def analyze_image(self, image_path: Path) -> Dict[str, any]:
        """
        Analyze a single image for quality assessment using advanced techniques.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Calculate various quality metrics with enhanced algorithms
            blur_score = self._calculate_enhanced_blur_score(image)
            brightness_score = self._calculate_enhanced_brightness_score(image)
            contrast_score = self._calculate_enhanced_contrast_score(image)
            edge_score = self._calculate_enhanced_edge_score(image)
            saturation_score = self._calculate_enhanced_saturation_score(image)
            noise_score = self._calculate_noise_score(image)
            composition_score = self._calculate_composition_score(image)
            
            # Calculate overall quality score with enhanced weighting
            quality_score = self._calculate_enhanced_overall_score(
                blur_score, brightness_score, contrast_score, 
                edge_score, saturation_score, noise_score, composition_score
            )
            
            # Determine if image is good or bad based on quality threshold
            is_good_image = self._enhanced_classification(
                quality_score, blur_score, brightness_score, contrast_score,
                noise_score, edge_score, saturation_score
            )
            
            # Categorize image based on visual characteristics
            category = self._enhanced_categorization(
                blur_score, brightness_score, contrast_score, 
                edge_score, saturation_score, noise_score, composition_score
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
                    'saturation_score': saturation_score,
                    'noise_score': noise_score,
                    'composition_score': composition_score
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze {image_path}: {e}")
            return {
                'path': str(image_path),
                'is_good': False,
                'error': str(e)
            }
    
    def _calculate_enhanced_blur_score(self, image: Image.Image) -> float:
        """Calculate enhanced blur score using multiple techniques."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Method 2: Sobel edge detection
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            sobel_var = np.var(sobel_magnitude)
            
            # Method 3: FFT-based blur detection
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # Calculate high-frequency content
            rows, cols = gray.shape
            crow, ccol = rows//2, cols//2
            high_freq = magnitude_spectrum[crow-30:crow+30, ccol-30:ccol+30]
            fft_score = np.mean(high_freq)
            
            # Combine all methods
            blur_score = (
                0.4 * min(1.0, np.log(laplacian_var + 1) / 10) +
                0.3 * min(1.0, np.log(sobel_var + 1) / 8) +
                0.3 * min(1.0, fft_score / 10)
            )
            
            return min(1.0, max(0.0, blur_score))
            
        except Exception:
            return 0.5
    
    def _calculate_enhanced_brightness_score(self, image: Image.Image) -> float:
        """Calculate enhanced brightness score with histogram analysis."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            gray_array = np.array(gray)
            
            # Calculate mean brightness
            mean_brightness = np.mean(gray_array) / 255.0
            
            # Calculate histogram-based brightness
            hist = cv2.calcHist([gray_array], [0], None, [256], [0, 256])
            hist_norm = hist.ravel() / hist.sum()
            
            # Calculate weighted brightness (center-weighted)
            weighted_brightness = np.sum(hist_norm * np.arange(256)) / 255.0
            
            # Combine mean and weighted brightness
            brightness_score = 0.6 * mean_brightness + 0.4 * weighted_brightness
            
            return min(1.0, max(0.0, brightness_score))
            
        except Exception:
            return 0.5
    
    def _calculate_enhanced_contrast_score(self, image: Image.Image) -> float:
        """Calculate enhanced contrast score with multiple metrics."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            gray_array = np.array(gray)
            
            # Method 1: Standard deviation
            std_contrast = np.std(gray_array) / 255.0
            
            # Method 2: Histogram spread
            hist = cv2.calcHist([gray_array], [0], None, [256], [0, 256])
            hist_norm = hist.ravel() / hist.sum()
            
            # Calculate histogram entropy (measure of contrast)
            hist_entropy = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
            entropy_contrast = min(1.0, hist_entropy / 8.0)  # Normalize to 0-1
            
            # Method 3: Local contrast using Laplacian
            laplacian = cv2.Laplacian(gray_array, cv2.CV_64F)
            local_contrast = np.std(laplacian) / 255.0
            
            # Combine all methods
            contrast_score = (
                0.4 * min(1.0, std_contrast * 2) +
                0.3 * entropy_contrast +
                0.3 * min(1.0, local_contrast * 0.5)
            )
            
            return min(1.0, max(0.0, contrast_score))
            
        except Exception:
            return 0.5
    
    def _calculate_enhanced_edge_score(self, image: Image.Image) -> float:
        """Calculate enhanced edge score with multiple edge detection methods."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Canny edge detection
            edges_canny = cv2.Canny(gray, 50, 150)
            edge_density_canny = np.sum(edges_canny > 0) / (edges_canny.shape[0] * edges_canny.shape[1])
            
            # Method 2: Sobel edge detection
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            edge_density_sobel = np.mean(sobel_magnitude > np.percentile(sobel_magnitude, 90))
            
            # Method 3: Laplacian edge detection
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            edge_density_laplacian = np.mean(np.abs(laplacian) > np.percentile(np.abs(laplacian), 90))
            
            # Combine all methods
            edge_score = (
                0.4 * min(1.0, edge_density_canny * 100) +
                0.3 * min(1.0, edge_density_sobel * 10) +
                0.3 * min(1.0, edge_density_laplacian * 10)
            )
            
            return min(1.0, max(0.0, edge_score))
            
        except Exception:
            return 0.5
    
    def _calculate_enhanced_saturation_score(self, image: Image.Image) -> float:
        """Calculate enhanced saturation score with color analysis."""
        try:
            # Convert to HSV color space
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Extract saturation channel
            saturation = hsv[:, :, 1]
            
            # Calculate mean saturation
            mean_saturation = np.mean(saturation) / 255.0
            
            # Calculate saturation variance (color diversity)
            saturation_variance = np.var(saturation) / (255.0 ** 2)
            
            # Calculate colorfulness (distance from gray)
            lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
            a_channel = lab[:, :, 1] - 128
            b_channel = lab[:, :, 2] - 128
            colorfulness = np.sqrt(np.mean(a_channel**2 + b_channel**2)) / 128.0
            
            # Combine all metrics
            saturation_score = (
                0.5 * mean_saturation +
                0.3 * min(1.0, saturation_variance * 10) +
                0.2 * min(1.0, colorfulness)
            )
            
            return min(1.0, max(0.0, saturation_score))
            
        except Exception:
            return 0.5
    
    def _calculate_noise_score(self, image: Image.Image) -> float:
        """Calculate noise level in the image."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            gray_array = np.array(gray)
            
            # Apply Gaussian blur to get smooth version
            smooth = cv2.GaussianBlur(gray_array, (5, 5), 0)
            
            # Calculate noise as difference between original and smooth
            noise = np.abs(gray_array.astype(float) - smooth.astype(float))
            noise_level = np.mean(noise) / 255.0
            
            # Convert to quality score (lower noise = higher score)
            noise_score = max(0.0, 1.0 - noise_level * 3)
            
            return min(1.0, max(0.0, noise_score))
            
        except Exception:
            return 0.5
    
    def _calculate_composition_score(self, image: Image.Image) -> float:
        """Calculate composition quality using rule of thirds and symmetry."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            gray_array = np.array(gray)
            
            height, width = gray_array.shape
            
            # Rule of thirds analysis
            third_h = height // 3
            third_w = width // 3
            
            # Calculate interest at intersection points
            intersections = [
                gray_array[third_h, third_w],
                gray_array[third_h, 2*third_w],
                gray_array[2*third_h, third_w],
                gray_array[2*third_h, 2*third_w]
            ]
            
            # Calculate variance at intersection points (higher variance = more interesting)
            intersection_variance = np.var(intersections) / 255.0
            
            # Symmetry analysis
            left_half = gray_array[:, :width//2]
            right_half = np.fliplr(gray_array[:, width//2:])
            
            # Calculate symmetry score
            symmetry_diff = np.mean(np.abs(left_half - right_half)) / 255.0
            symmetry_score = max(0.0, 1.0 - symmetry_diff)
            
            # Combine composition metrics
            composition_score = (
                0.6 * min(1.0, intersection_variance * 5) +
                0.4 * symmetry_score
            )
            
            return min(1.0, max(0.0, composition_score))
            
        except Exception:
            return 0.5
    
    def _calculate_enhanced_overall_score(self, blur_score: float, brightness_score: float, 
                                        contrast_score: float, edge_score: float, 
                                        saturation_score: float, noise_score: float,
                                        composition_score: float) -> float:
        """Calculate enhanced overall quality score with sophisticated weighting."""
        # Enhanced weights based on importance for photo quality
        weights = {
            'blur': 0.25,        # Sharpness is crucial
            'brightness': 0.15,  # Proper exposure
            'contrast': 0.15,    # Good contrast
            'edge': 0.15,        # Edge detection for structure
            'saturation': 0.10,  # Color quality
            'noise': 0.10,       # Image cleanliness
            'composition': 0.10  # Visual appeal
        }
        
        overall_score = (
            blur_score * weights['blur'] +
            brightness_score * weights['brightness'] +
            contrast_score * weights['contrast'] +
            edge_score * weights['edge'] +
            saturation_score * weights['saturation'] +
            noise_score * weights['noise'] +
            composition_score * weights['composition']
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def _enhanced_classification(self, quality_score: float, blur_score: float, 
                                brightness_score: float, contrast_score: float,
                                noise_score: float, edge_score: float, 
                                saturation_score: float) -> bool:
        """Enhanced classification with multiple criteria."""
        # Check individual thresholds
        if blur_score < 0.25:  # Too blurry
            return False
        if brightness_score < 0.15 or brightness_score > 0.85:  # Too dark or too bright
            return False
        if contrast_score < 0.25:  # Too low contrast
            return False
        if noise_score < 0.3:  # Too noisy
            return False
        
        # Check for document/screenshot characteristics
        if edge_score > 0.8 and contrast_score > 0.7:  # High edge density + contrast = likely document
            return False
        if saturation_score < 0.2 and brightness_score > 0.6:  # Low saturation + high brightness = likely screenshot
            return False
        
        # Use overall quality score
        return quality_score >= self.quality_threshold
    
    def _enhanced_categorization(self, blur_score: float, brightness_score: float, 
                                contrast_score: float, edge_score: float, 
                                saturation_score: float, noise_score: float,
                                composition_score: float) -> str:
        """Enhanced categorization with more detailed analysis."""
        # Document detection
        if edge_score > 0.7 and contrast_score > 0.6:
            return 'document'
        
        # Screenshot detection
        if saturation_score < 0.25 and brightness_score > 0.6:
            return 'screenshot'
        
        # Very blurry images
        if blur_score < 0.2:
            return 'blurry'
        
        # Noisy images
        if noise_score < 0.3:
            return 'noisy'
        
        # Excellent quality images
        if (blur_score > 0.7 and contrast_score > 0.6 and 
            noise_score > 0.6 and composition_score > 0.5):
            return 'excellent_quality'
        
        # Good quality images
        if blur_score > 0.5 and contrast_score > 0.4:
            return 'good_quality'
        
        # Low contrast images
        if contrast_score < 0.3:
            return 'low_contrast'
        
        return 'other'
    
    def analyze_batch(self, image_paths: List[Path]) -> Dict[str, List]:
        """
        Analyze multiple images in batch with enhanced algorithms.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary with 'good' and 'bad' image lists
        """
        logger.info(f"🔍 Analyzing {len(image_paths)} images with enhanced computer vision...")
        
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
        logger.info("🧹 Enhanced AI Image Analyzer resources cleaned up")


def create_analyzer(device: str = "auto", confidence_threshold: float = 0.7):
    """Factory function to create an enhanced image analyzer."""
    return EnhancedImageAnalyzer(device=device, quality_threshold=confidence_threshold)
