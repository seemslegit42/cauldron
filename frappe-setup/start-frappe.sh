#!/bin/bash
# Script to start the Frappe server

set -e

# Default values
CONTAINER_NAME="frappe-web"
SITE_NAME="cauldron.local"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --container)
      CONTAINER_NAME="$2"
      shift
      shift
      ;;
    --site-name)
      SITE_NAME="$2"
      shift
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --site-name NAME        Site name (default: cauldron.local)"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Starting Frappe server in container: $CONTAINER_NAME"
echo "Site: $SITE_NAME"

# Set the site as default
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && bench use $SITE_NAME"

# Start the Frappe server
docker exec -it -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && bench start"
