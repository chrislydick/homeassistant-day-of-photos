#!/usr/bin/env python3
"""
AI Image Analyzer with Local LLM
Uses a local LLM to describe photo content and evaluate if it's good for a photo frame
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import cv2
import base64
import io
import json

logger = logging.getLogger(__name__)

class LLMImageAnalyzer:
    """Image analyzer using local LLM for content description and evaluation."""
    
    def __init__(self, device: str = "auto", quality_threshold: float = 0.6):
        """
        Initialize the LLM image analyzer.
        
        Args:
            device: Device to use ('auto', 'cuda', 'cpu') - kept for compatibility
            quality_threshold: Quality score threshold for good/bad classification (0.0-1.0)
        """
        self.quality_threshold = quality_threshold
        self.device = device
        self.llm_client = None
        self.vision_model = None
        
        # Initialize LLM and vision model
        self._initialize_models()
        
        logger.info("🚀 LLM Image Analyzer initialized with local models")
    
    def _initialize_models(self):
        """Initialize the LLM and vision models."""
        try:
            # Try to import and initialize local LLM
            self._setup_llm()
            self._setup_vision_model()
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize models: {e}")
            logger.info("ℹ️ Will use fallback analysis methods")
    
    def _setup_llm(self):
        """Setup local LLM (Ollama, LM Studio, etc.) with GPU support."""
        try:
            # Try Ollama first (most common for local LLMs)
            import requests
            
            # Test if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    # Check for GPU support
                    gpu_info = self._check_gpu_support()
                    if gpu_info:
                        logger.info(f"✅ Ollama detected and running with GPU support: {gpu_info}")
                    else:
                        logger.info("✅ Ollama detected and running (CPU mode)")
                    self.llm_client = "ollama"
                    return
            except:
                pass
            
            # Try LM Studio
            try:
                response = requests.get("http://localhost:1234/v1/models", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ LM Studio detected and running")
                    self.llm_client = "lmstudio"
                    return
            except:
                pass
            
            # Try other local LLM servers
            logger.info("ℹ️ No local LLM server detected")
            
        except ImportError:
            logger.warning("⚠️ Requests not available for LLM communication")
    
    def _check_gpu_support(self):
        """Check if GPU is available and being used by Ollama."""
        try:
            import subprocess
            import json
            
            # Check if nvidia-smi is available
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(',')
                if len(gpu_info) >= 3:
                    gpu_name = gpu_info[0].strip()
                    total_memory = int(gpu_info[1].strip())
                    used_memory = int(gpu_info[2].strip())
                    return f"{gpu_name} ({used_memory}/{total_memory} MB used)"
            
            return None
            
        except Exception as e:
            logger.debug(f"GPU check failed: {e}")
            return None
    
    def _setup_vision_model(self):
        """Setup vision model for image description."""
        try:
            # Try to use a local vision model
            # For now, we'll use basic OpenCV features as fallback
            logger.info("ℹ️ Using OpenCV-based vision analysis")
            self.vision_model = "opencv"
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup vision model: {e}")
    
    def _describe_image_opencv(self, image: Image.Image) -> str:
        """Describe image using OpenCV features."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Basic image analysis
            height, width = gray.shape
            aspect_ratio = width / height
            
            # Calculate basic features
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Color analysis
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1])
            
            # Determine image type based on features
            description = f"Image analysis: {width}x{height} pixels, "
            description += f"brightness: {brightness:.0f}, contrast: {contrast:.0f}, "
            description += f"edge density: {edge_density:.3f}, saturation: {saturation:.0f}. "
            
            # Classify image type
            if edge_density > 0.1 and contrast > 50:
                description += "High detail image with strong edges and contrast."
            elif saturation < 50:
                description += "Low saturation, possibly grayscale or screenshot."
            elif brightness < 50:
                description += "Dark image with low brightness."
            elif brightness > 200:
                description += "Very bright or overexposed image."
            else:
                description += "Standard photograph with balanced features."
            
            return description
            
        except Exception as e:
            return f"Error analyzing image: {e}"
    
    def _query_llm(self, prompt: str, image_base64: str = None) -> str:
        """Query the local LLM with text and optionally an image."""
        try:
            if self.llm_client == "ollama":
                return self._query_ollama(prompt, image_base64)
            elif self.llm_client == "lmstudio":
                return self._query_lmstudio(prompt, image_base64)
            else:
                # Fallback: use rule-based analysis
                return self._rule_based_analysis(prompt)
                
        except Exception as e:
            logger.warning(f"⚠️ LLM query failed: {e}")
            return self._rule_based_analysis(prompt)
    
    def _query_ollama(self, prompt: str, image_base64: str = None) -> str:
        """Query Ollama LLM with GPU optimization."""
        import requests
        
        url = "http://localhost:11434/api/generate"
        
        # Get model from environment or use default (vision-capable model)
        model = os.getenv("LLM_MODEL", "llava:7b")
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_gpu": 1,  # Use GPU
                "num_thread": 8,  # Optimize thread count
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        if image_base64:
            data["images"] = [image_base64]
        
        try:
            response = requests.post(url, json=data, timeout=60)  # Increased timeout for GPU processing
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        except requests.exceptions.Timeout:
            logger.warning("⚠️ Ollama request timed out, trying with CPU fallback")
            # Fallback to CPU mode
            data["options"]["num_gpu"] = 0
            response = requests.post(url, json=data, timeout=120)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
    
    def _query_lmstudio(self, prompt: str, image_base64: str = None) -> str:
        """Query LM Studio LLM."""
        import requests
        
        url = "http://localhost:1234/v1/chat/completions"
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": "local-model",  # or your specific model
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"LM Studio API error: {response.status_code}")
    
    def _rule_based_analysis(self, description: str) -> str:
        """Fallback rule-based analysis when LLM is not available."""
        description_lower = description.lower()
        
        # Check for problematic content
        if any(word in description_lower for word in ["qr code", "barcode", "document", "paper", "text", "screenshot"]):
            return "BAD: Contains QR codes, documents, or text-heavy content not suitable for photo frame display."
        
        if any(word in description_lower for word in ["dark", "blurry", "overexposed", "low contrast"]):
            return "BAD: Poor image quality with technical issues."
        
        if any(word in description_lower for word in ["person", "people", "pet", "animal", "landscape", "scenery", "nature"]):
            return "GOOD: Contains people, pets, or scenic content suitable for photo frame display."
        
        return "NEUTRAL: Standard photograph, quality depends on technical characteristics."
    
    def _evaluate_for_photo_frame(self, description: str, llm_response: str) -> Tuple[bool, float, str]:
        """Evaluate if image is good for photo frame display."""
        try:
            # Combine description and LLM response
            full_analysis = f"Image: {description}\nLLM Analysis: {llm_response}"
            
            # Determine if it's good based on LLM response
            llm_response_lower = llm_response.lower()
            
            if "good" in llm_response_lower or "suitable" in llm_response_lower:
                is_good = True
                score = 0.8
                category = "good_photo"
            elif "bad" in llm_response_lower or "not suitable" in llm_response_lower:
                is_good = False
                score = 0.2
                category = "unsuitable_content"
            else:
                # Neutral response, use technical analysis
                is_good = self._technical_quality_check(description)
                score = 0.5 if is_good else 0.3
                category = "neutral_quality"
            
            return is_good, score, category
            
        except Exception as e:
            logger.warning(f"⚠️ Evaluation failed: {e}")
            return False, 0.0, "error"
    
    def _technical_quality_check(self, description: str) -> bool:
        """Check technical quality when LLM response is neutral."""
        description_lower = description.lower()
        
        # Check for good technical characteristics
        good_indicators = ["balanced", "standard photograph", "high detail"]
        bad_indicators = ["dark", "blurry", "overexposed", "low contrast", "low saturation"]
        
        good_score = sum(1 for indicator in good_indicators if indicator in description_lower)
        bad_score = sum(1 for indicator in bad_indicators if indicator in description_lower)
        
        return good_score > bad_score
    
    def analyze_image(self, image_path: Path) -> Dict[str, any]:
        """
        Analyze a single image using LLM and vision models.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Get image description
            description = self._describe_image_opencv(image)
            
            # Convert image to base64 for LLM (if needed)
            image_base64 = None
            if self.llm_client:
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG')
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Create prompt for LLM
            prompt = f"""Analyze this image and determine if it would be good to display on a photo frame in a home.

Consider:
- Is it a personal photo (people, pets, family moments)?
- Is it scenic or beautiful (landscapes, nature, architecture)?
- Does it contain inappropriate content (documents, QR codes, screenshots, text)?
- Is it technically good quality (not too dark, blurry, or overexposed)?

Respond with either "GOOD: [reason]" or "BAD: [reason]" and provide a brief explanation."""

            # Query LLM
            llm_response = self._query_llm(prompt, image_base64)
            
            # Evaluate for photo frame
            is_good, score, category = self._evaluate_for_photo_frame(description, llm_response)
            
            return {
                'path': str(image_path),
                'is_good': is_good,
                'quality_score': score,
                'category': category,
                'description': description,
                'llm_response': llm_response,
                'analysis': {
                    'description': description,
                    'llm_response': llm_response,
                    'category': category
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze {image_path}: {e}")
            return {
                'path': str(image_path),
                'is_good': False,
                'error': str(e)
            }
    
    def analyze_batch(self, image_paths: List[Path]) -> Dict[str, List]:
        """
        Analyze multiple images in batch.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary with 'good' and 'bad' image lists
        """
        logger.info(f"🔍 Analyzing {len(image_paths)} images with LLM vision analysis...")
        
        good_images = []
        bad_images = []
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"📸 Analyzing image {i+1}/{len(image_paths)}: {image_path.name}")
            
            result = self.analyze_image(image_path)
            
            if result.get('is_good', False):
                good_images.append(result)
                logger.info(f"✅ GOOD image: {image_path.name} (score: {result.get('quality_score', 0):.2f})")
                if 'llm_response' in result:
                    logger.info(f"   💬 LLM: {result['llm_response'][:100]}...")
            else:
                bad_images.append(result)
                logger.info(f"❌ BAD image: {image_path.name} (score: {result.get('quality_score', 0):.2f})")
                if 'llm_response' in result:
                    logger.info(f"   💬 LLM: {result['llm_response'][:100]}...")
        
        logger.info(f"🎯 Analysis complete: {len(good_images)} good, {len(bad_images)} bad images")
        
        return {
            'good': good_images,
            'bad': bad_images,
            'total': len(image_paths)
        }
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("🧹 LLM Image Analyzer resources cleaned up")


def create_analyzer(device: str = "auto", confidence_threshold: float = 0.7):
    """Factory function to create an LLM image analyzer."""
    return LLMImageAnalyzer(device=device, quality_threshold=confidence_threshold)
