#!/bin/bash
# Script to set up RBAC roles in a Frappe application

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

echo "Setting up RBAC roles with the following configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  Site: $SITE_NAME"
echo ""

# Copy the Python script to the container
echo "Copying RBAC setup script to container..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR=$(mktemp -d)

# Copy the Python script to the temp directory
cp "$SCRIPT_DIR/setup-rbac-roles.py" "$TEMP_DIR/"

# Create a wrapper script to run the Python script in the Frappe environment
cat > "$TEMP_DIR/run_setup_rbac.py" << EOF
#!/usr/bin/env python3
import os
import sys
import frappe

def run_setup_script():
    """Run the RBAC setup script in the Frappe environment"""
    try:
        # Execute the setup script
        exec(open('/tmp/rbac_setup/setup-rbac-roles.py').read())
        return True
    except Exception as e:
        print(f"Error running RBAC setup script: {str(e)}")
        return False

if __name__ == "__main__":
    frappe.init(site="$SITE_NAME")
    frappe.connect()
    
    try:
        result = run_setup_script()
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        frappe.destroy()
EOF

# Copy the files to the container
docker cp "$TEMP_DIR" "$CONTAINER_NAME:/tmp/rbac_setup"

# Make the scripts executable
docker exec "$CONTAINER_NAME" bash -c "chmod +x /tmp/rbac_setup/*.py"

# Run the script in the container
echo "Setting up RBAC roles in the container..."
docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && python /tmp/rbac_setup/run_setup_rbac.py"

# Clean up
rm -rf "$TEMP_DIR"

echo "RBAC roles setup completed successfully!"
echo ""
echo "The following roles have been created:"
echo "  - Cauldron Admin: Full administrative access"
echo "  - Cauldron Finance User: Access to financial modules"
echo "  - Cauldron Dev User: Access to development tools"
echo "  - Cauldron Operator: Day-to-day operational access"
echo "  - Cauldron Agent: Limited API access for automated agents"
echo "  - Cauldron Read Only: Read-only access to view data"
echo "  - Cauldron Customer: Limited access for external customers"
echo "  - Cauldron Supplier: Limited access for suppliers"
echo ""
echo "The following role profiles have been created:"
echo "  - Cauldron Administrator: Admin role"
echo "  - Cauldron Finance Manager: Finance User + Read Only roles"
echo "  - Cauldron Developer: Dev User + Read Only roles"
echo "  - Cauldron Operations: Operator + Read Only roles"
echo "  - Cauldron API Integration: Agent role"
