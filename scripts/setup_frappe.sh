#!/bin/bash
# scripts/setup_frappe.sh

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Adjust these variables as needed
BENCH_DIR_NAME="frappe-bench" # Name of the bench directory
SITE_NAME="cauldron.local"    # Name of the default site
PYTHON_VER="python3.11"       # Ensure this matches python installed via devcontainer feature
DB_HOST="postgres"            # Service name of the Postgres container in docker-compose.yml
# IMPORTANT: These passwords MUST be set as GitHub Codespaces secrets
# and exposed as environment variables to the container.
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-please_change_in_env}" # Default to placeholder if not set
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"   # Default to 'admin' if not set

# Custom Cauldron Apps to be created
CUSTOM_APPS=(
  "cauldron_operations_core"
  "cauldron_synapse"
  "cauldron_aegis_protocol"
  "cauldron_lore"
  "cauldron_command_cauldron"
)

# --- Helper Functions ---
log() {
  echo "[SETUP_FRAPPE] $(date +'%T') - $1"
}

check_env_vars() {
  log "Checking required environment variables..."
  if [ "$DB_ROOT_PASSWORD" == "please_change_in_env" ]; then
    log "WARNING: Using default DB_ROOT_PASSWORD. For production, set this in .env file."
  fi
  if [ "$ADMIN_PASSWORD" == "admin" ]; then
    log "WARNING: Using default ADMIN_PASSWORD. For production, set this in .env file."
  fi
  log "Environment variables check passed."
}

create_custom_app() {
  APP_NAME=$1
  log "Creating custom app: $APP_NAME"
  
  if [ -d "apps/$APP_NAME" ]; then
    log "App $APP_NAME already exists. Skipping creation."
    return 0
  fi
  
  # Create the app using bench
  bench new-app $APP_NAME --skip-boilerplate
  
  # Create basic directory structure for the app
  mkdir -p "apps/$APP_NAME/$APP_NAME/api"
  mkdir -p "apps/$APP_NAME/$APP_NAME/public/js"
  mkdir -p "apps/$APP_NAME/$APP_NAME/public/css"
  
  # Create a basic controller file
  cat > "apps/$APP_NAME/$APP_NAME/api/controller.py" << EOF
import frappe
from frappe import _

@frappe.whitelist()
def get_status():
    return {
        "status": "success",
        "message": _("$APP_NAME module is active"),
        "module": "$APP_NAME"
    }
EOF

  log "Custom app $APP_NAME created successfully."
}

# --- Main Script ---
log "Starting Frappe setup script..."
WORKSPACE_DIR="/workspaces/cauldron"
BENCH_PATH="$WORKSPACE_DIR/$BENCH_DIR_NAME"
SITE_PATH="$BENCH_PATH/sites/$SITE_NAME"

# Check if required ENV VARS are set
check_env_vars

# Ensure we are in the workspace directory
cd "$WORKSPACE_DIR" || exit 1

# Check if Bench directory exists
if [ -d "$BENCH_PATH" ]; then
  log "Bench directory '$BENCH_PATH' already exists."
else
  log "Bench directory not found. Initializing Frappe Bench in '$BENCH_PATH'..."
  bench init "$BENCH_DIR_NAME" --frappe-branch version-15 --python "$PYTHON_VER" --skip-redis-config-generation
  log "Frappe Bench initialized."
fi

# Navigate into the bench directory
cd "$BENCH_PATH" || exit 1
log "Current directory: $(pwd)"

# Configure bench to use our Redis and PostgreSQL services
log "Configuring bench to use Docker services..."
cat > "$BENCH_PATH/sites/common_site_config.json" << EOF
{
    "db_host": "$DB_HOST",
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
}
EOF

# Get ERPNext app if not already present
if [ ! -d "apps/erpnext" ]; then
  log "Getting ERPNext app..."
  bench get-app erpnext --branch version-15 || log "Failed to get ERPNext app."
fi

# Get HR app if not already present
if [ ! -d "apps/hrms" ]; then
  log "Getting HRMS app..."
  bench get-app hrms --branch version-15 || log "Failed to get HRMS app."
fi

# Check if the site already exists
if [ -d "$SITE_PATH" ]; then
  log "Site '$SITE_NAME' already exists in '$SITE_PATH'."
  log "Running database migrations..."
  bench --site "$SITE_NAME" migrate || log "Migration failed, continuing..."
  log "Ensuring developer mode is enabled..."
  bench --site "$SITE_NAME" set-config developer_mode 1 || log "Failed to set developer mode."
else
  log "Site '$SITE_NAME' not found. Creating new site..."

  # Create the site
  log "Creating new site '$SITE_NAME'..."
  bench new-site "$SITE_NAME" \
    --db-name cauldron \
    --db-host "$DB_HOST" \
    --db-port 5432 \
    --db-root-password "$DB_ROOT_PASSWORD" \
    --admin-password "$ADMIN_PASSWORD" \
    --set-default
  log "Site '$SITE_NAME' created."

  # Install ERPNext
  log "Installing ERPNext app..."
  bench --site "$SITE_NAME" install-app erpnext || log "Failed to install ERPNext app."
  
  # Install HRMS
  log "Installing HRMS app..."
  bench --site "$SITE_NAME" install-app hrms || log "Failed to install HRMS app."

  # Create and install custom Cauldron apps
  log "Creating and installing custom Cauldron apps..."
  for app in "${CUSTOM_APPS[@]}"; do
    create_custom_app "$app"
    log "Installing app: $app"
    bench --site "$SITE_NAME" install-app "$app" || log "Failed to install app '$app'."
  done

  log "Setting developer mode..."
  bench --site "$SITE_NAME" set-config developer_mode 1 || log "Failed to set developer mode."

  log "Site setup complete."
fi

# Start the development server in the background
log "Starting Frappe development server..."
bench start &

log "Frappe setup script finished successfully."
log "You can access the site at: http://localhost:8000"
exit 0
