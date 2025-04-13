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
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-}" # Default to empty if not set
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"   # Default to empty if not set

# Custom Cauldron Apps (Assume they are already cloned/present in ./apps directory relative to bench)
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
  if [ -z "$DB_ROOT_PASSWORD" ]; then
    log "ERROR: DB_ROOT_PASSWORD environment variable is not set. Please configure it in Codespaces secrets."
    exit 1
  fi
  if [ -z "$ADMIN_PASSWORD" ]; then
    log "ERROR: ADMIN_PASSWORD environment variable is not set. Please configure it in Codespaces secrets."
    exit 1
  fi
  log "Environment variables check passed."
}

# --- Main Script ---
log "Starting Frappe setup script..."
WORKSPACE_DIR="/workspaces/cauldron-sEOS"
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

# Check if the site already exists
if [ -d "$SITE_PATH" ]; then
  log "Site '$SITE_NAME' already exists in '$SITE_PATH'."
  log "Running database migrations..."
  bench --site "$SITE_NAME" migrate || log "Migration failed, continuing..."
  log "Ensuring developer mode is enabled..."
  bench --site "$SITE_NAME" set-config developer_mode 1 || log "Failed to set developer mode."
else
  log "Site '$SITE_NAME' not found. Creating new site..."

  log "Getting ERPNext app..."
  bench get-app erpnext --branch version-15 || log "Failed to get ERPNext app."

  log "Checking for custom apps in ./apps directory..."
  # Ensure custom apps are already in frappe-bench/apps/ via git submodules or other means

  log "Creating new site '$SITE_NAME'..."
  bench new-site "$SITE_NAME" \
    --db-name cauldron \
    --db-host "$DB_HOST" \
    --db-port 5432 \
    --db-root-password "$DB_ROOT_PASSWORD" \
    --admin-password "$ADMIN_PASSWORD" \
    --install-app erpnext \
    --set-default
  log "Site '$SITE_NAME' created."

  log "Installing custom Cauldron apps..."
  for app in "${CUSTOM_APPS[@]}"; do
    if [ -d "apps/$app" ]; then
      log "Installing app: $app"
      bench --site "$SITE_NAME" install-app "$app" || log "Failed to install app '$app'."
    else
      log "WARNING: Custom app '$app' not found in ./apps directory. Skipping installation."
      log "Ensure custom apps are placed in $BENCH_PATH/apps before running this script."
    fi
  done

  log "Setting developer mode..."
  bench --site "$SITE_NAME" set-config developer_mode 1 || log "Failed to set developer mode."

  log "Site setup complete."
fi

log "Frappe setup script finished."
exit 0
