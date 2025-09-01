#!/usr/bin/env python3
"""
AI Image Analyzer for Photo Quality Assessment
Uses pre-trained models to identify good vs bad images
Optimized for NVIDIA Jetson Orin
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import cv2
import torch
import torch.nn.functional as F
from torchvision import transforms, models
from torchvision.models import ResNet50_Weights

logger = logging.getLogger(__name__)

class AIImageAnalyzer:
    """AI-powered image analyzer for photo quality assessment."""
    
    def __init__(self, device: str = "auto", confidence_threshold: float = 0.7):
        """
        Initialize the AI image analyzer.
        
        Args:
            device: Device to use ('auto', 'cuda', 'cpu')
            confidence_threshold: Minimum confidence for classification
        """
        self.confidence_threshold = confidence_threshold
        self.device = self._setup_device(device)
        self.model = None
        self.transform = None
        self.class_names = []
        
        # Initialize models
        self._setup_models()
        
        logger.info(f"🚀 AI Image Analyzer initialized on {self.device}")
    
    def _setup_device(self, device: str) -> str:
        """Setup the best available device."""
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                logger.info("✅ CUDA available, using GPU acceleration")
            else:
                device = "cpu"
                logger.info("ℹ️ CUDA not available, using CPU")
        return device
    
    def _setup_models(self):
        """Setup pre-trained models for image analysis."""
        try:
            # Load pre-trained ResNet50 for general image classification
            self.model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
            self.model.eval()
            self.model.to(self.device)
            
            # Setup image transformations
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            # Get ImageNet class names
            self.class_names = ResNet50_Weights.IMAGENET1K_V2.meta["categories"]
            
            logger.info("✅ ResNet50 model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load AI models: {e}")
            raise
    
    def analyze_image(self, image_path: Path) -> Dict[str, any]:
        """
        Analyze a single image for quality assessment.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = F.softmax(outputs, dim=1)
                top_probs, top_indices = torch.topk(probabilities, 5)
            
            # Extract top predictions
            top_predictions = []
            for prob, idx in zip(top_probs[0], top_indices[0]):
                class_name = self.class_names[idx]
                confidence = prob.item()
                top_predictions.append({
                    'class': class_name,
                    'confidence': confidence
                })
            
            # Analyze image characteristics
            quality_score = self._calculate_quality_score(image, top_predictions)
            is_good_image = self._classify_image_quality(top_predictions, quality_score)
            
            # Determine image category
            category = self._categorize_image(top_predictions)
            
            return {
                'path': str(image_path),
                'is_good': is_good_image,
                'quality_score': quality_score,
                'category': category,
                'top_predictions': top_predictions,
                'analysis': {
                    'blur_score': self._calculate_blur_score(image),
                    'brightness_score': self._calculate_brightness_score(image),
                    'contrast_score': self._calculate_contrast_score(image)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze {image_path}: {e}")
            return {
                'path': str(image_path),
                'is_good': False,
                'error': str(e)
            }
    
    def _calculate_quality_score(self, image: Image.Image, predictions: List[Dict]) -> float:
        """Calculate overall image quality score."""
        # Base score from model confidence
        base_score = sum(p['confidence'] for p in predictions[:3]) / 3
        
        # Boost score for desirable categories
        desirable_keywords = [
            'person', 'people', 'human', 'face', 'portrait', 'family',
            'pet', 'dog', 'cat', 'animal', 'wildlife',
            'landscape', 'nature', 'scenery', 'mountain', 'beach', 'forest',
            'building', 'architecture', 'city', 'street'
        ]
        
        boost = 0.0
        for pred in predictions[:3]:
            if any(keyword in pred['class'].lower() for keyword in desirable_keywords):
                boost += 0.1
        
        # Penalize for undesirable categories
        undesirable_keywords = [
            'whiteboard', 'blackboard', 'chalkboard',
            'document', 'text', 'writing', 'handwriting',
            'screenshot', 'computer', 'monitor', 'screen',
            'blur', 'noise', 'grain'
        ]
        
        penalty = 0.0
        for pred in predictions[:3]:
            if any(keyword in pred['class'].lower() for keyword in undesirable_keywords):
                penalty += 0.2
        
        final_score = min(1.0, max(0.0, base_score + boost - penalty))
        return final_score
    
    def _classify_image_quality(self, predictions: List[Dict], quality_score: float) -> bool:
        """Classify whether an image is good or bad."""
        # Check if any top predictions are clearly undesirable
        clearly_bad = [
            'whiteboard', 'blackboard', 'chalkboard',
            'document', 'text', 'writing', 'handwriting',
            'screenshot', 'computer', 'monitor', 'screen'
        ]
        
        for pred in predictions[:2]:
            if any(bad in pred['class'].lower() for bad in clearly_bad):
                return False
        
        # Use quality score threshold
        return quality_score >= self.confidence_threshold
    
    def _categorize_image(self, predictions: List[Dict]) -> str:
        """Categorize the type of image."""
        top_pred = predictions[0]['class'].lower()
        
        if any(word in top_pred for word in ['person', 'people', 'human', 'face']):
            return 'people'
        elif any(word in top_pred for word in ['dog', 'cat', 'pet', 'animal']):
            return 'pets'
        elif any(word in top_pred for word in ['landscape', 'nature', 'scenery', 'mountain']):
            return 'scenery'
        elif any(word in top_pred for word in ['building', 'architecture', 'city']):
            return 'architecture'
        elif any(word in top_pred for word in ['whiteboard', 'document', 'text']):
            return 'document'
        elif any(word in top_pred for word in ['screenshot', 'computer', 'monitor']):
            return 'screenshot'
        else:
            return 'other'
    
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
        """Clean up resources."""
        if self.model is not None:
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("🧹 AI Image Analyzer resources cleaned up")


def create_analyzer(device: str = "auto", confidence_threshold: float = 0.7) -> AIImageAnalyzer:
    """Factory function to create an AI image analyzer."""
    return AIImageAnalyzer(device=device, confidence_threshold=confidence_threshold)
