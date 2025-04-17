#!/bin/bash
# Script to update the common_site_config.json file

set -e

# Default values
CONTAINER_NAME="frappe-web"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --container)
      CONTAINER_NAME="$2"
      shift
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Updating common_site_config.json in container: $CONTAINER_NAME"

# Create the updated common_site_config.json
CONFIG_JSON='{
    "db_host": "postgres",
    "db_port": 5432,
    "redis_cache": "redis://redis-cache:6379/0",
    "redis_queue": "redis://redis-queue:6379/1",
    "redis_socketio": "redis://redis-socketio:6379/2",
    "socketio_port": 9000,
    "webserver_port": 8000,
    "developer_mode": 1,
    "serve_default_site": true,
    "auto_update": false,
    "frappe_user": "frappe",
    "shallow_clone": true
}'

# Update the common_site_config.json file in the container
docker exec -u frappe "$CONTAINER_NAME" bash -c "echo '$CONFIG_JSON' > /home/frappe/frappe-bench/sites/common_site_config.json"

echo "common_site_config.json updated successfully!"
