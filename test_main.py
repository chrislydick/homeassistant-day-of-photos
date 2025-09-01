#!/usr/bin/env python3
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_script():
    logger.info("🚀 Testing main script import...")
    try:
        import onedrive_photos_script_enhanced
        logger.info("✅ Main script imported successfully")
        
        # Test if AI_AVAILABLE is defined
        if hasattr(onedrive_photos_script_enhanced, 'AI_AVAILABLE'):
            logger.info(f"✅ AI_AVAILABLE: {onedrive_photos_script_enhanced.AI_AVAILABLE}")
        else:
            logger.warning("⚠️ AI_AVAILABLE not found")
            
    except Exception as e:
        logger.error(f"❌ Failed to import main script: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_script()
