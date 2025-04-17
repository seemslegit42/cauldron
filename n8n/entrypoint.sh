#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log "Waiting for PostgreSQL to be ready..."
    until PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_POSTGRESDB_HOST:-postgres} -U ${DB_POSTGRESDB_USER:-postgres} -c '\q'; do
        log "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    log "PostgreSQL is up - continuing"
}

# Main execution
log "Starting n8n container..."

# Wait for dependencies
wait_for_postgres

# Check if database exists, if not create it
if ! PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_POSTGRESDB_HOST:-postgres} -U ${DB_POSTGRESDB_USER:-postgres} -lqt | cut -d \| -f 1 | grep -qw "${DB_POSTGRESDB_DATABASE:-n8n}"; then
    log "Creating database: ${DB_POSTGRESDB_DATABASE:-n8n}"
    PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_POSTGRESDB_HOST:-postgres} -U ${DB_POSTGRESDB_USER:-postgres} -c "CREATE DATABASE \"${DB_POSTGRESDB_DATABASE:-n8n}\";"
    log "Database created."
fi

# Start n8n
log "Starting n8n..."
exec n8n start
