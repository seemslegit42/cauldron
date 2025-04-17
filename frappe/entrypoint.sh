#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log "Waiting for PostgreSQL to be ready..."
    until PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_HOST:-postgres} -U postgres -c '\q'; do
        log "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    log "PostgreSQL is up - continuing"
}

# Wait for Redis services to be ready
wait_for_redis() {
    local redis_host=$1
    local redis_port=$2
    log "Waiting for Redis at $redis_host:$redis_port to be ready..."
    until redis-cli -h $redis_host -p $redis_port ping; do
        log "Redis at $redis_host:$redis_port is unavailable - sleeping"
        sleep 1
    done
    log "Redis at $redis_host:$redis_port is up - continuing"
}

# Main execution
log "Starting Frappe container..."

# Wait for dependencies
wait_for_postgres
wait_for_redis redis-cache 6379
wait_for_redis redis-queue 6379
wait_for_redis redis-socketio 6379

# Check if site exists, if not create it
if [ ! -f sites/${SITE_NAME:-cauldron.local}/site_config.json ]; then
    log "Creating new site: ${SITE_NAME:-cauldron.local}"
    bench new-site ${SITE_NAME:-cauldron.local} \
        --admin-password ${ADMIN_PASSWORD:-admin} \
        --db-host ${DB_HOST:-postgres} \
        --db-name ${DB_NAME:-frappe} \
        --db-password ${DB_ROOT_PASSWORD:-please_change_in_env} \
        --db-type postgres \
        --no-mariadb-socket
    
    # Install ERPNext and other apps if needed
    log "Installing ERPNext app..."
    bench get-app --branch version-14 erpnext
    bench --site ${SITE_NAME:-cauldron.local} install-app erpnext
    
    # Install custom Cauldron apps if they exist
    for app in cauldron_operations_core cauldron_synapse cauldron_aegis_protocol cauldron_lore cauldron_command_cauldron; do
        if [ -d apps/$app ]; then
            log "Installing $app app..."
            bench --site ${SITE_NAME:-cauldron.local} install-app $app
        fi
    done
    
    log "Site setup completed."
fi

# Set site as default
bench use ${SITE_NAME:-cauldron.local}

# Execute the command passed to docker
log "Executing command: $@"
exec "$@"
