#!/bin/bash
# Script to create a new custom Frappe app

set -e

# Default values
CONTAINER_NAME="frappe-web"
SITE_NAME="cauldron.local"
APP_NAME=""

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
    --app-name)
      APP_NAME="$2"
      shift
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --site-name NAME        Site name (default: cauldron.local)"
      echo "  --app-name NAME         App name (required)"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check if app name is provided
if [ -z "$APP_NAME" ]; then
  echo "Error: App name is required"
  echo "Usage: $0 --app-name NAME"
  exit 1
fi

echo "Creating new Frappe app: $APP_NAME"
echo "Container: $CONTAINER_NAME"
echo "Site: $SITE_NAME"

# Create the app
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && bench new-app $APP_NAME"

# Install the app
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && bench --site $SITE_NAME install-app $APP_NAME"

echo "App $APP_NAME created and installed successfully!"
echo ""
echo "You can now start developing your app in the apps/$APP_NAME directory."
echo "To access the app, navigate to: http://localhost:8000/app/$APP_NAME"
