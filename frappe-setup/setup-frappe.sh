#!/bin/bash
# Script to install the base Frappe framework within its container environment

set -e

# Default values
CONTAINER_NAME="frappe-web"
FRAPPE_VERSION="version-15"
ERPNEXT_VERSION="version-15"
SITE_NAME="cauldron.local"
ADMIN_PASSWORD="admin"
INSTALL_ERPNEXT=true
INSTALL_CUSTOM_APPS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --container)
      CONTAINER_NAME="$2"
      shift
      shift
      ;;
    --frappe-version)
      FRAPPE_VERSION="$2"
      shift
      shift
      ;;
    --erpnext-version)
      ERPNEXT_VERSION="$2"
      shift
      shift
      ;;
    --site-name)
      SITE_NAME="$2"
      shift
      shift
      ;;
    --admin-password)
      ADMIN_PASSWORD="$2"
      shift
      shift
      ;;
    --skip-erpnext)
      INSTALL_ERPNEXT=false
      shift
      ;;
    --install-custom-apps)
      INSTALL_CUSTOM_APPS=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --frappe-version VER    Frappe version/branch (default: version-15)"
      echo "  --erpnext-version VER   ERPNext version/branch (default: version-15)"
      echo "  --site-name NAME        Site name (default: cauldron.local)"
      echo "  --admin-password PASS   Admin password (default: admin)"
      echo "  --skip-erpnext          Skip ERPNext installation"
      echo "  --install-custom-apps   Install custom Cauldron apps"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Starting Frappe installation with the following configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  Frappe Version: $FRAPPE_VERSION"
echo "  ERPNext Version: $ERPNEXT_VERSION"
echo "  Site Name: $SITE_NAME"
echo "  Install ERPNext: $INSTALL_ERPNEXT"
echo "  Install Custom Apps: $INSTALL_CUSTOM_APPS"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not accessible"
  exit 1
fi

# Check if the container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
  echo "Error: Container '$CONTAINER_NAME' does not exist"
  echo "Please run 'docker-compose up -d' first"
  exit 1
fi

# Function to execute commands in the container
execute_in_container() {
  docker exec -u frappe "$CONTAINER_NAME" bash -c "$1"
}

# Step 1: Install Frappe framework
echo "Step 1: Installing Frappe framework..."
execute_in_container "cd /home/frappe/frappe-bench && bench get-app --branch $FRAPPE_VERSION frappe"

# Step 2: Create a new site
echo "Step 2: Creating a new site..."
execute_in_container "cd /home/frappe/frappe-bench && bench new-site $SITE_NAME --admin-password $ADMIN_PASSWORD --db-host postgres --db-name frappe --db-password \$DB_ROOT_PASSWORD --db-type postgres --no-mariadb-socket"

# Step 3: Install ERPNext (if not skipped)
if [ "$INSTALL_ERPNEXT" = true ]; then
  echo "Step 3: Installing ERPNext..."
  execute_in_container "cd /home/frappe/frappe-bench && bench get-app --branch $ERPNEXT_VERSION erpnext"
  execute_in_container "cd /home/frappe/frappe-bench && bench --site $SITE_NAME install-app erpnext"
fi

# Step 4: Install custom Cauldron apps (if requested)
if [ "$INSTALL_CUSTOM_APPS" = true ]; then
  echo "Step 4: Installing custom Cauldron apps..."
  
  # Define the custom apps to install
  CUSTOM_APPS=(
    "cauldron_operations_core:https://github.com/seemslegit42/cauldron_operations_core.git:main"
    "cauldron_synapse:https://github.com/seemslegit42/cauldron_synapse.git:main"
    "cauldron_aegis_protocol:https://github.com/seemslegit42/cauldron_aegis_protocol.git:main"
    "cauldron_lore:https://github.com/seemslegit42/cauldron_lore.git:main"
    "cauldron_command_cauldron:https://github.com/seemslegit42/cauldron_command_cauldron.git:main"
  )
  
  for app_info in "${CUSTOM_APPS[@]}"; do
    IFS=':' read -r app_name app_repo app_branch <<< "$app_info"
    echo "  Installing $app_name from $app_repo ($app_branch)..."
    execute_in_container "cd /home/frappe/frappe-bench && bench get-app --branch $app_branch $app_name $app_repo"
    execute_in_container "cd /home/frappe/frappe-bench && bench --site $SITE_NAME install-app $app_name"
  done
fi

# Step 5: Set site as default and enable developer mode
echo "Step 5: Configuring site..."
execute_in_container "cd /home/frappe/frappe-bench && bench use $SITE_NAME"
execute_in_container "cd /home/frappe/frappe-bench && bench --site $SITE_NAME set-config developer_mode 1"

# Step 6: Build assets
echo "Step 6: Building assets..."
execute_in_container "cd /home/frappe/frappe-bench && bench build"

echo "Frappe installation completed successfully!"
echo ""
echo "To start the Frappe server, run:"
echo "  docker exec -it $CONTAINER_NAME bash -c 'cd /home/frappe/frappe-bench && bench start'"
echo ""
echo "You can access the Frappe site at: http://localhost:8000"
echo "Login with:"
echo "  Username: Administrator"
echo "  Password: $ADMIN_PASSWORD"
