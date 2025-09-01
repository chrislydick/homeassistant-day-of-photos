#!/usr/bin/env python3
"""
Test script for AI Image Analyzer
"""

import logging
from pathlib import Path
from ai_image_analyzer import create_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_ai_analyzer():
    """Test the AI image analyzer with sample images."""
    logger = logging.getLogger(__name__)
    
    logger.info("🧪 Testing AI Image Analyzer...")
    
    try:
        # Create analyzer
        analyzer = create_analyzer(device="auto", confidence_threshold=0.6)
        
        # Test with a sample image if available
        test_image = Path("./test_image.jpg")
        
        if test_image.exists():
            logger.info(f"📸 Testing with image: {test_image}")
            result = analyzer.analyze_image(test_image)
            
            logger.info("📊 Analysis Results:")
            logger.info(f"   Path: {result['path']}")
            logger.info(f"   Is Good: {result['is_good']}")
            logger.info(f"   Quality Score: {result.get('quality_score', 0):.3f}")
            logger.info(f"   Category: {result.get('category', 'unknown')}")
            
            if 'top_predictions' in result:
                logger.info("   Top Predictions:")
                for i, pred in enumerate(result['top_predictions'][:3]):
                    logger.info(f"     {i+1}. {pred['class']} ({pred['confidence']:.3f})")
            
            if 'analysis' in result:
                logger.info("   Technical Analysis:")
                logger.info(f"     Blur Score: {result['analysis'].get('blur_score', 0):.3f}")
                logger.info(f"     Brightness: {result['analysis'].get('brightness_score', 0):.3f}")
                logger.info(f"     Contrast: {result['analysis'].get('contrast_score', 0):.3f}")
        
        else:
            logger.info("ℹ️ No test image found. Create a test_image.jpg to test the analyzer.")
            logger.info("✅ AI Image Analyzer initialization successful!")
        
        # Clean up
        analyzer.cleanup()
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_ai_analyzer()
    if success:
        print("🎉 AI Image Analyzer test completed successfully!")
    else:
        print("❌ AI Image Analyzer test failed!")
        exit(1)
