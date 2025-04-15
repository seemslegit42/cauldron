#!/usr/bin/env python3
"""
Run API Script for AetherCore

This script runs the AetherCore API using uvicorn.
"""

import os
import sys
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_api():
    """Run the AetherCore API"""
    try:
        # Get configuration from environment
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", 8000))
        debug = os.environ.get("DEBUG", "False").lower() == "true"
        
        # Run uvicorn
        uvicorn.run(
            "aether_core.api.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="debug" if debug else "info"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error running API: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting AetherCore API...")
    success = run_api()
    
    if not success:
        logger.error("API startup failed")
        sys.exit(1)