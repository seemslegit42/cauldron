#!/bin/bash
# Script to set up core permissions for Frappe DocTypes

# Configuration
SITE_NAME=${1:-"cauldron.local"}
CONTAINER_NAME=${2:-"cauldron-frappe"}

# Display banner
echo "=================================================="
echo "  Setting up Core Permissions for Frappe DocTypes  "
echo "=================================================="
echo ""
echo "Site: $SITE_NAME"
echo "Container: $CONTAINER_NAME"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or not accessible."
    exit 1
fi

# Check if the container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Error: Container $CONTAINER_NAME does not exist."
    exit 1
fi

# Check if the container is running
if ! docker ps --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Error: Container $CONTAINER_NAME is not running."
    exit 1
fi

# Copy the Python script to the container
echo "Copying setup script to container..."
docker cp "$(dirname "$0")/setup-core-permissions.py" "$CONTAINER_NAME:/tmp/setup-core-permissions.py"

# Make the script executable
docker exec "$CONTAINER_NAME" bash -c "chmod +x /tmp/setup-core-permissions.py"

# Run the script in the container
echo "Setting up core permissions in the container..."
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && python3 /tmp/setup-core-permissions.py"

# Clean up
docker exec "$CONTAINER_NAME" bash -c "rm -f /tmp/setup-core-permissions.py"

echo ""
echo "Core permissions setup completed!"
echo ""
echo "The following roles now have appropriate permissions on core Frappe DocTypes:"
echo "  - Cauldron Admin: Full access to all core DocTypes"
echo "  - Cauldron Finance User: Limited access to relevant DocTypes"
echo "  - Cauldron Dev User: Access to development-related DocTypes"
echo "  - Cauldron Operator: Day-to-day operational access"
echo "  - Cauldron Agent: Limited API access for automated agents"
echo "  - Cauldron Read Only: Read-only access to all DocTypes"
echo "  - Cauldron Customer: Limited access for external customers"
echo "  - Cauldron Supplier: Limited access for suppliers"
echo ""
