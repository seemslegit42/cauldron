#!/bin/bash
# Script to configure Frappe to connect to PostgreSQL

set -e

# Default values
CONTAINER_NAME="frappe-web"
SITE_NAME="cauldron.local"
DB_HOST="postgres"
DB_PORT="5432"
DB_NAME="frappe"
DB_USER="postgres"
DB_PASSWORD=""
FORCE_RECONFIGURE=false

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
    --db-host)
      DB_HOST="$2"
      shift
      shift
      ;;
    --db-port)
      DB_PORT="$2"
      shift
      shift
      ;;
    --db-name)
      DB_NAME="$2"
      shift
      shift
      ;;
    --db-user)
      DB_USER="$2"
      shift
      shift
      ;;
    --db-password)
      DB_PASSWORD="$2"
      shift
      shift
      ;;
    --force)
      FORCE_RECONFIGURE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --container NAME        Container name (default: frappe-web)"
      echo "  --site-name NAME        Site name (default: cauldron.local)"
      echo "  --db-host HOST          Database host (default: postgres)"
      echo "  --db-port PORT          Database port (default: 5432)"
      echo "  --db-name NAME          Database name (default: frappe)"
      echo "  --db-user USER          Database user (default: postgres)"
      echo "  --db-password PASS      Database password (required if not set in environment)"
      echo "  --force                 Force reconfiguration even if already configured"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# If DB_PASSWORD is not provided, try to get it from environment variable
if [ -z "$DB_PASSWORD" ]; then
  if [ -n "$DB_ROOT_PASSWORD" ]; then
    DB_PASSWORD="$DB_ROOT_PASSWORD"
  else
    echo "Error: Database password is required"
    echo "Please provide it using --db-password or set the DB_ROOT_PASSWORD environment variable"
    exit 1
  fi
fi

echo "Configuring Frappe to connect to PostgreSQL with the following settings:"
echo "  Container: $CONTAINER_NAME"
echo "  Site: $SITE_NAME"
echo "  Database Host: $DB_HOST"
echo "  Database Port: $DB_PORT"
echo "  Database Name: $DB_NAME"
echo "  Database User: $DB_USER"
echo ""

# Function to execute commands in the container
execute_in_container() {
  docker exec -u frappe "$CONTAINER_NAME" bash -c "$1"
}

# Step 1: Update common_site_config.json
echo "Step 1: Updating common_site_config.json..."

# Get current config if it exists
CONFIG_EXISTS=$(docker exec -u frappe "$CONTAINER_NAME" bash -c "[ -f /home/frappe/frappe-bench/sites/common_site_config.json ] && echo 'true' || echo 'false'")

if [ "$CONFIG_EXISTS" = "true" ] && [ "$FORCE_RECONFIGURE" = "false" ]; then
  echo "  common_site_config.json already exists. Updating..."
  # Get current config
  CURRENT_CONFIG=$(docker exec -u frappe "$CONTAINER_NAME" bash -c "cat /home/frappe/frappe-bench/sites/common_site_config.json")
  
  # Create a temporary file with the updated config
  TMP_FILE=$(mktemp)
  echo "$CURRENT_CONFIG" > "$TMP_FILE"
  
  # Update the database settings
  python3 -c "
import json
import sys

# Load the current config
with open('$TMP_FILE', 'r') as f:
    config = json.load(f)

# Update the database settings
config['db_host'] = '$DB_HOST'
config['db_port'] = $DB_PORT
config['db_name'] = '$DB_NAME'
config['db_user'] = '$DB_USER'

# Write the updated config
with open('$TMP_FILE', 'w') as f:
    json.dump(config, f, indent=4)
"
  
  # Copy the updated config back to the container
  docker cp "$TMP_FILE" "$CONTAINER_NAME:/home/frappe/frappe-bench/sites/common_site_config.json"
  
  # Clean up
  rm "$TMP_FILE"
else
  echo "  Creating new common_site_config.json..."
  # Create the updated common_site_config.json
  CONFIG_JSON='{
    "db_host": "'$DB_HOST'",
    "db_port": '$DB_PORT',
    "db_name": "'$DB_NAME'",
    "db_user": "'$DB_USER'",
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
  execute_in_container "echo '$CONFIG_JSON' > /home/frappe/frappe-bench/sites/common_site_config.json"
fi

# Step 2: Update site_config.json
echo "Step 2: Updating site_config.json..."

# Check if site exists
SITE_EXISTS=$(docker exec -u frappe "$CONTAINER_NAME" bash -c "[ -d /home/frappe/frappe-bench/sites/$SITE_NAME ] && echo 'true' || echo 'false'")

if [ "$SITE_EXISTS" = "true" ]; then
  echo "  Site $SITE_NAME exists. Updating site_config.json..."
  
  # Get current site config
  SITE_CONFIG_EXISTS=$(docker exec -u frappe "$CONTAINER_NAME" bash -c "[ -f /home/frappe/frappe-bench/sites/$SITE_NAME/site_config.json ] && echo 'true' || echo 'false'")
  
  if [ "$SITE_CONFIG_EXISTS" = "true" ]; then
    # Get current site config
    CURRENT_SITE_CONFIG=$(docker exec -u frappe "$CONTAINER_NAME" bash -c "cat /home/frappe/frappe-bench/sites/$SITE_NAME/site_config.json")
    
    # Create a temporary file with the updated config
    TMP_SITE_FILE=$(mktemp)
    echo "$CURRENT_SITE_CONFIG" > "$TMP_SITE_FILE"
    
    # Update the database settings
    python3 -c "
import json
import sys

# Load the current config
with open('$TMP_SITE_FILE', 'r') as f:
    config = json.load(f)

# Update the database settings
config['db_host'] = '$DB_HOST'
config['db_port'] = $DB_PORT
config['db_name'] = '$DB_NAME'
config['db_user'] = '$DB_USER'
config['db_password'] = '$DB_PASSWORD'

# Write the updated config
with open('$TMP_SITE_FILE', 'w') as f:
    json.dump(config, f, indent=4)
"
    
    # Copy the updated config back to the container
    docker cp "$TMP_SITE_FILE" "$CONTAINER_NAME:/home/frappe/frappe-bench/sites/$SITE_NAME/site_config.json"
    
    # Clean up
    rm "$TMP_SITE_FILE"
  else
    echo "  Creating new site_config.json..."
    # Create the site_config.json
    SITE_CONFIG_JSON='{
    "db_host": "'$DB_HOST'",
    "db_port": '$DB_PORT',
    "db_name": "'$DB_NAME'",
    "db_user": "'$DB_USER'",
    "db_password": "'$DB_PASSWORD'"
}'
    
    # Update the site_config.json file in the container
    execute_in_container "echo '$SITE_CONFIG_JSON' > /home/frappe/frappe-bench/sites/$SITE_NAME/site_config.json"
  fi
else
  echo "  Site $SITE_NAME does not exist. Please create it first using setup-frappe.sh."
  exit 1
fi

# Step 3: Test the database connection
echo "Step 3: Testing the database connection..."

# Test the connection
CONNECTION_TEST=$(docker exec -u frappe "$CONTAINER_NAME" bash -c "cd /home/frappe/frappe-bench && bench --site $SITE_NAME console <<< \"frappe.db.get_value('User', 'Administrator', 'name')\"")

if [[ $CONNECTION_TEST == *"Administrator"* ]]; then
  echo "  Database connection successful!"
else
  echo "  Database connection failed. Please check your settings."
  echo "  Error: $CONNECTION_TEST"
  exit 1
fi

echo "PostgreSQL configuration completed successfully!"
echo ""
echo "To start the Frappe server, run:"
echo "  ./start-frappe.sh --site-name $SITE_NAME"
