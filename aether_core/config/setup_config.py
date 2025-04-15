#!/usr/bin/env python3
"""
Configuration setup script for AetherCore

This script replaces environment variable placeholders in configuration files
with their actual values from the environment.
"""

import os
import json
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def replace_env_vars(config_path):
    """
    Replace environment variable placeholders in a configuration file
    with their actual values from the environment.
    
    Args:
        config_path (str): Path to the configuration file
    """
    try:
        # Read the configuration file
        with open(config_path, 'r') as f:
            config = f.read()
        
        # Find all environment variable placeholders
        env_vars = re.findall(r'\${([A-Za-z0-9_]+)}', config)
        
        # Replace each placeholder with its value
        for var in env_vars:
            value = os.environ.get(var, '')
            config = config.replace('${' + var + '}', value)
        
        # Write the updated configuration back to the file
        with open(config_path, 'w') as f:
            f.write(config)
        
        logger.info(f"Successfully updated configuration in {config_path}")
        
        # Validate JSON if it's a JSON file
        if config_path.endswith('.json'):
            try:
                json.loads(config)
                logger.info(f"JSON validation successful for {config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {config_path}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error updating configuration in {config_path}: {str(e)}")

if __name__ == "__main__":
    # Update SuperAGI configuration
    superagi_config_path = os.environ.get('SUPERAGI_CONFIG_PATH', '/app/config/superagi_config.json')
    replace_env_vars(superagi_config_path)