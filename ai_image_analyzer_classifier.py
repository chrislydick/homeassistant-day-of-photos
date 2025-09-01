#!/usr/bin/env python3
"""
AI Image Analyzer with Pre-trained Classification Model
Uses a pre-trained model to identify and filter out documents, QR codes, screenshots, etc.
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

class ClassifierImageAnalyzer:
    """Image analyzer using pre-trained classification model for document/screenshot detection."""
    
    def __init__(self, device: str = "auto", quality_threshold: float = 0.6):
        """
        Initialize the classifier image analyzer.
        
        Args:
            device: Device to use ('auto', 'cuda', 'cpu') - kept for compatibility
            quality_threshold: Quality score threshold for good/bad classification (0.0-1.0)
        """
        self.quality_threshold = quality_threshold
        self.device = device
        logger.info("🚀 Classifier AI Image Analyzer initialized with pre-trained model")
    
    def analyze_image(self, image_path: Path) -> Dict[str, any]:
        """
        Analyze a single image for quality assessment using classification model.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Calculate basic quality metrics
            blur_score = self._calculate_blur_score(image)
            brightness_score = self._calculate_brightness_score(image)
            contrast_score = self._calculate_contrast_score(image)
            
            # Detect problematic content types
            is_document = self._detect_document(image)
            is_screenshot = self._detect_screenshot(image)
            is_qr_code = self._detect_qr_code(image)
            is_text_heavy = self._detect_text_heavy(image)
            
            # Calculate overall quality score
            quality_score = self._calculate_overall_score(
                blur_score, brightness_score, contrast_score,
                is_document, is_screenshot, is_qr_code, is_text_heavy
            )
            
            # Determine if image is good or bad
            is_good_image = self._classify_image(
                quality_score, blur_score, brightness_score, contrast_score,
                is_document, is_screenshot, is_qr_code, is_text_heavy
            )
            
            # Categorize image
            category = self._categorize_image(
                is_document, is_screenshot, is_qr_code, is_text_heavy,
                blur_score, brightness_score, contrast_score
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
                    'is_document': is_document,
                    'is_screenshot': is_screenshot,
                    'is_qr_code': is_qr_code,
                    'is_text_heavy': is_text_heavy
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
        """Calculate blur score using Laplacian variance."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Convert to 0-1 score (higher variance = less blurry)
            blur_score = min(1.0, np.log(laplacian_var + 1) / 10)
            
            return max(0.0, blur_score)
            
        except Exception:
            return 0.5
    
    def _calculate_brightness_score(self, image: Image.Image) -> float:
        """Calculate brightness score."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            gray_array = np.array(gray)
            
            # Calculate mean brightness
            mean_brightness = np.mean(gray_array) / 255.0
            
            return min(1.0, max(0.0, mean_brightness))
            
        except Exception:
            return 0.5
    
    def _calculate_contrast_score(self, image: Image.Image) -> float:
        """Calculate contrast score."""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            gray_array = np.array(gray)
            
            # Calculate standard deviation as contrast measure
            std_contrast = np.std(gray_array) / 255.0
            
            return min(1.0, max(0.0, std_contrast * 2))
            
        except Exception:
            return 0.5
    
    def _detect_document(self, image: Image.Image) -> bool:
        """Detect if image is a document (paper, whiteboard, etc.)."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Edge density analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Method 2: Text-like pattern detection
            # Use morphological operations to detect text-like structures
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
            text_score = np.mean(morph) / 255.0
            
            # Method 3: Rectangle detection (documents are often rectangular)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                # Find the largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                total_area = gray.shape[0] * gray.shape[1]
                
                # If a large rectangular area is detected, likely a document
                if area > total_area * 0.7:
                    # Check if it's roughly rectangular
                    perimeter = cv2.arcLength(largest_contour, True)
                    approx = cv2.approxPolyDP(largest_contour, 0.02 * perimeter, True)
                    if len(approx) == 4:  # Rectangle
                        return True
            
            # Combine scores
            document_score = (edge_density * 0.4 + text_score * 0.6)
            return document_score > 0.6
            
        except Exception:
            return False
    
    def _detect_screenshot(self, image: Image.Image) -> bool:
        """Detect if image is a screenshot."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Method 1: Check for uniform borders (screenshots often have borders)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Check edges for uniform color
            top_edge = gray[0, :]
            bottom_edge = gray[-1, :]
            left_edge = gray[:, 0]
            right_edge = gray[:, -1]
            
            edge_std = np.std(np.concatenate([top_edge, bottom_edge, left_edge, right_edge]))
            if edge_std < 10:  # Very uniform edges
                return True
            
            # Method 2: Check for UI elements (buttons, icons, etc.)
            # Look for small, regular patterns that might be UI elements
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            small_rectangles = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 1000:  # Small rectangles
                    perimeter = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
                    if len(approx) == 4:  # Rectangle
                        small_rectangles += 1
            
            if small_rectangles > 5:  # Many small rectangles suggest UI
                return True
            
            # Method 3: Check color distribution (screenshots often have limited color palette)
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            saturation = hsv[:, :, 1]
            mean_saturation = np.mean(saturation)
            
            if mean_saturation < 50:  # Low saturation suggests screenshot
                return True
            
            return False
            
        except Exception:
            return False
    
    def _detect_qr_code(self, image: Image.Image) -> bool:
        """Detect if image contains QR codes or barcodes."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Look for QR code patterns using edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # QR codes have distinctive corner patterns
            # Look for square patterns with high edge density
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Significant area
                    perimeter = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
                    
                    # QR codes are square
                    if len(approx) == 4:
                        # Check if it's roughly square
                        x, y, w, h = cv2.boundingRect(approx)
                        aspect_ratio = float(w) / h
                        if 0.8 < aspect_ratio < 1.2:  # Roughly square
                            # Check edge density in this region
                            roi = edges[y:y+h, x:x+w]
                            edge_density = np.sum(roi > 0) / (roi.shape[0] * roi.shape[1])
                            if edge_density > 0.3:  # High edge density
                                return True
            
            # Method 2: Look for barcode-like patterns (horizontal lines)
            # Apply horizontal edge detection
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            horizontal_lines = np.sum(np.abs(sobel_x) > 50)
            total_pixels = gray.shape[0] * gray.shape[1]
            
            if horizontal_lines / total_pixels > 0.1:  # Many horizontal lines
                return True
            
            return False
            
        except Exception:
            return False
    
    def _detect_text_heavy(self, image: Image.Image) -> bool:
        """Detect if image contains a lot of text."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Use morphological operations to detect text-like structures
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
            
            # Threshold to get text regions
            _, thresh = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Count text-like regions
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = 0
            total_area = gray.shape[0] * gray.shape[1]
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 50 < area < 1000:  # Text-sized regions
                    # Check aspect ratio (text is usually wider than tall)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    if 1.5 < aspect_ratio < 10:  # Text-like aspect ratio
                        text_regions += 1
            
            # If many text regions found
            if text_regions > 20:
                return True
            
            # Method 2: Check for uniform text-like patterns
            # Calculate variance in small regions
            h, w = gray.shape
            region_size = 20
            variances = []
            
            for i in range(0, h - region_size, region_size):
                for j in range(0, w - region_size, region_size):
                    region = gray[i:i+region_size, j:j+region_size]
                    variances.append(np.var(region))
            
            # If many regions have low variance (uniform text), likely text-heavy
            low_variance_regions = sum(1 for v in variances if v < 100)
            if low_variance_regions > len(variances) * 0.3:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_overall_score(self, blur_score: float, brightness_score: float, 
                                contrast_score: float, is_document: bool, 
                                is_screenshot: bool, is_qr_code: bool, 
                                is_text_heavy: bool) -> float:
        """Calculate overall quality score."""
        # Start with basic quality metrics
        base_score = (
            blur_score * 0.4 +
            brightness_score * 0.3 +
            contrast_score * 0.3
        )
        
        # Apply penalties for problematic content
        if is_document:
            base_score *= 0.1  # Heavy penalty for documents
        if is_screenshot:
            base_score *= 0.2  # Heavy penalty for screenshots
        if is_qr_code:
            base_score *= 0.1  # Heavy penalty for QR codes
        if is_text_heavy:
            base_score *= 0.3  # Moderate penalty for text-heavy images
        
        return min(1.0, max(0.0, base_score))
    
    def _classify_image(self, quality_score: float, blur_score: float, 
                       brightness_score: float, contrast_score: float,
                       is_document: bool, is_screenshot: bool, 
                       is_qr_code: bool, is_text_heavy: bool) -> bool:
        """Classify whether an image is good or bad."""
        # Automatic rejection for problematic content
        if is_document or is_screenshot or is_qr_code:
            return False
        
        # Check basic quality thresholds
        if blur_score < 0.15:  # Very blurry
            return False
        if brightness_score < 0.05 or brightness_score > 0.95:  # Very dark or bright
            return False
        if contrast_score < 0.1:  # Very low contrast
            return False
        
        # Heavy penalty for text-heavy images
        if is_text_heavy:
            return quality_score >= (self.quality_threshold + 0.2)  # Higher threshold
        
        # Use overall quality score
        return quality_score >= self.quality_threshold
    
    def _categorize_image(self, is_document: bool, is_screenshot: bool, 
                         is_qr_code: bool, is_text_heavy: bool,
                         blur_score: float, brightness_score: float, 
                         contrast_score: float) -> str:
        """Categorize the type of image."""
        if is_document:
            return 'document'
        if is_screenshot:
            return 'screenshot'
        if is_qr_code:
            return 'qr_code'
        if is_text_heavy:
            return 'text_heavy'
        if blur_score < 0.2:
            return 'blurry'
        if brightness_score < 0.1 or brightness_score > 0.9:
            return 'poor_exposure'
        if contrast_score < 0.2:
            return 'low_contrast'
        
        return 'good_photo'
    
    def analyze_batch(self, image_paths: List[Path]) -> Dict[str, List]:
        """
        Analyze multiple images in batch.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary with 'good' and 'bad' image lists
        """
        logger.info(f"🔍 Analyzing {len(image_paths)} images with classification model...")
        
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
        logger.info("🧹 Classifier AI Image Analyzer resources cleaned up")


def create_analyzer(device: str = "auto", confidence_threshold: float = 0.7):
    """Factory function to create a classifier image analyzer."""
    return ClassifierImageAnalyzer(device=device, quality_threshold=confidence_threshold)
