#!/bin/bash
# Script to install the Invoice DocType in a Frappe application

set -e

# Default values
CONTAINER_NAME="frappe-web"
SITE_NAME="cauldron.local"
APP_NAME="cauldron_operations_core"
MODULE_NAME="Accounts"

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
    --module-name)
      MODULE_NAME="$2"
      shift
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --site-name NAME        Site name (default: cauldron.local)"
      echo "  --app-name NAME         App name (default: cauldron_operations_core)"
      echo "  --module-name NAME      Module name (default: Accounts)"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Installing Invoice DocType with the following configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  Site: $SITE_NAME"
echo "  App: $APP_NAME"
echo "  Module: $MODULE_NAME"
echo ""

# Copy the DocType files to the container
echo "Copying DocType files to container..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCTYPES_DIR="$SCRIPT_DIR/doctypes"
TEMP_DIR=$(mktemp -d)

# Copy the files to the temp directory
cp "$SCRIPT_DIR/install-doctypes.py" "$TEMP_DIR/"
mkdir -p "$TEMP_DIR/doctypes"
cp "$DOCTYPES_DIR"/*.json "$TEMP_DIR/doctypes/"

# Copy the files to the container
docker cp "$TEMP_DIR" "$CONTAINER_NAME:/tmp/doctypes_install"

# Make the script executable
docker exec "$CONTAINER_NAME" bash -c "chmod +x /tmp/doctypes_install/install-doctypes.py"

# Run the script in the container
echo "Installing DocTypes in the container..."
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && python3 /tmp/doctypes_install/install-doctypes.py --app $APP_NAME --module '$MODULE_NAME' --site $SITE_NAME --bench-path /home/frappe/frappe-bench --doctypes-dir /tmp/doctypes_install/doctypes"

# Clean up
rm -rf "$TEMP_DIR"

echo "Invoice DocType installation completed successfully!"
echo ""
echo "You can now access the Invoice DocType in your Frappe application."
