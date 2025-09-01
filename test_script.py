#!/usr/bin/env python3
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Test script starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info("✅ Test script completed successfully")

if __name__ == "__main__":
    main()
