#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log "Waiting for PostgreSQL to be ready..."
    until PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_HOST:-postgres} -U postgres -c "\q"; do
        log "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    log "PostgreSQL is up - continuing"
}

# Wait for Qdrant to be ready
wait_for_qdrant() {
    log "Waiting for Qdrant to be ready..."
    until curl -s -f ${VECTOR_DB_URL:-http://qdrant:6333}/health > /dev/null; do
        log "Qdrant is unavailable - sleeping"
        sleep 2
    done
    log "Qdrant is up - continuing"
}

# Create database if it doesn't exist
create_database() {
    if ! PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_HOST:-postgres} -U postgres -lqt | cut -d \| -f 1 | grep -qw "superagi"; then
        log "Creating database: superagi"
        PGPASSWORD=${DB_ROOT_PASSWORD:-please_change_in_env} psql -h ${DB_HOST:-postgres} -U postgres -c "CREATE DATABASE superagi;"
        log "Database created."
    else
        log "Database already exists."
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    alembic upgrade head
    log "Migrations completed."
}

# Initialize custom extensions
initialize_custom_extensions() {
    if [ -d "/app/custom/extensions" ]; then
        log "Initializing custom extensions..."
        for ext in /app/custom/extensions/*; do
            if [ -d "$ext" ]; then
                log "Initializing extension: $(basename "$ext")"
                if [ -f "$ext/setup.py" ]; then
                    pip install -e "$ext"
                fi
                if [ -f "$ext/init.sh" ]; then
                    bash "$ext/init.sh"
                fi
            fi
        done
        log "Custom extensions initialized."
    fi
}

# Load custom configuration
load_custom_config() {
    if [ -f "/app/custom/config.json" ]; then
        log "Loading custom configuration..."
        cp /app/custom/config.json /app/config/config.json
        log "Custom configuration loaded."
    fi
}

# Main execution
log "Starting SuperAGI container..."

# Wait for dependencies
wait_for_postgres
wait_for_qdrant

# Setup database
create_database
run_migrations

# Initialize custom components
initialize_custom_extensions
load_custom_config

# Set environment-specific configurations
if [ "$ENVIRONMENT" = "prod" ]; then
    log "Running in production mode"
    export DEBUG=False
    export LOG_LEVEL=INFO
elif [ "$ENVIRONMENT" = "staging" ]; then
    log "Running in staging mode"
    export DEBUG=False
    export LOG_LEVEL=INFO
else
    log "Running in development mode"
    export DEBUG=True
    export LOG_LEVEL=DEBUG
fi

# Start the application
log "Starting SuperAGI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8080 --log-level ${LOG_LEVEL:-info}
