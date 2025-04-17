#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log "Waiting for PostgreSQL to be ready..."
    until PGPASSWORD=${POSTGRES_PASSWORD:-please_change_in_env} psql -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-postgres} -c '\q'; do
        log "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    log "PostgreSQL is up - continuing"
}

# Main execution
log "Starting Coder container..."

# Wait for dependencies if enabled
if [ "${WAIT_FOR_DB:-true}" = "true" ]; then
    wait_for_postgres
fi

# Check if database exists, if not create it
if [ "${CREATE_DB:-true}" = "true" ]; then
    log "Checking if database exists..."
    if ! PGPASSWORD=${POSTGRES_PASSWORD:-please_change_in_env} psql -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-postgres} -lqt | cut -d \| -f 1 | grep -qw "${POSTGRES_DB:-coder}"; then
        log "Creating database: ${POSTGRES_DB:-coder}"
        PGPASSWORD=${POSTGRES_PASSWORD:-please_change_in_env} psql -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-postgres} -c "CREATE DATABASE \"${POSTGRES_DB:-coder}\";"
        log "Database created."
    else
        log "Database already exists."
    fi
fi

# Set up Coder configuration
if [ ! -f "${CODER_CONFIG_DIR}/coder.env" ]; then
    log "Setting up Coder configuration..."
    
    # Create configuration directory if it doesn't exist
    mkdir -p ${CODER_CONFIG_DIR}
    
    # Create environment file
    cat > ${CODER_CONFIG_DIR}/coder.env << EOF
CODER_ACCESS_URL=${CODER_ACCESS_URL:-http://localhost:3000}
CODER_WILDCARD_ACCESS_URL=${CODER_WILDCARD_ACCESS_URL:-*.localhost}
CODER_PG_CONNECTION_URL=postgres://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-please_change_in_env}@${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-coder}?sslmode=disable
CODER_TELEMETRY_ENABLE=${CODER_TELEMETRY_ENABLE:-false}
CODER_CACHE_DIRECTORY=${CODER_CACHE_DIRECTORY:-/var/cache/coder}
CODER_PROMETHEUS_ENABLE=${CODER_PROMETHEUS_ENABLE:-true}
CODER_PROMETHEUS_ADDRESS=${CODER_PROMETHEUS_ADDRESS:-0.0.0.0:2112}
CODER_HTTP_ADDRESS=${CODER_HTTP_ADDRESS:-0.0.0.0:3000}
EOF
    
    log "Coder configuration created."
fi

# Start Coder server
log "Starting Coder server..."
exec coder server --config-file=${CODER_CONFIG_DIR}/coder.env
