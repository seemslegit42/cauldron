"""
Initialization Script for AetherCore

This script initializes the AetherCore database and creates the default agent hierarchy.
"""

import os
import sys
import logging
import requests
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# AetherCore API URL
AETHERCORE_API_URL = os.environ.get("AETHERCORE_API_URL", "http://localhost:8000")


def wait_for_api_ready(max_retries=30, retry_interval=5):
    """Wait for the AetherCore API to be ready"""
    logger.info("Waiting for AetherCore API to be ready...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{AETHERCORE_API_URL}/health")
            if response.status_code == 200:
                logger.info("AetherCore API is ready!")
                return True
        except Exception as e:
            logger.debug(f"API not ready yet: {str(e)}")
        
        logger.info(f"Retrying in {retry_interval} seconds... ({i+1}/{max_retries})")
        time.sleep(retry_interval)
    
    logger.error("AetherCore API failed to become ready")
    return False


def initialize_agent_hierarchy():
    """Initialize the agent hierarchy"""
    logger.info("Initializing agent hierarchy...")
    
    try:
        response = requests.post(f"{AETHERCORE_API_URL}/api/v1/agents/hierarchy/initialize")
        
        if response.status_code == 200:
            logger.info("Agent hierarchy initialized successfully!")
            return True
        else:
            logger.error(f"Failed to initialize agent hierarchy: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error initializing agent hierarchy: {str(e)}")
        return False


def main():
    """Main initialization function"""
    logger.info("Starting AetherCore initialization...")
    
    # Wait for API to be ready
    if not wait_for_api_ready():
        logger.error("Initialization failed: API not ready")
        sys.exit(1)
    
    # Initialize agent hierarchy
    if not initialize_agent_hierarchy():
        logger.error("Initialization failed: Could not initialize agent hierarchy")
        sys.exit(1)
    
    logger.info("AetherCore initialization completed successfully!")


if __name__ == "__main__":
    main()