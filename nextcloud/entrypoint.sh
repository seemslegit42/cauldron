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

# Wait for Redis to be ready
wait_for_redis() {
    log "Waiting for Redis to be ready..."
    until redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping; do
        log "Redis is unavailable - sleeping"
        sleep 1
    done
    log "Redis is up - continuing"
}

# Main execution
log "Starting Nextcloud container..."

# Wait for dependencies if enabled
if [ "${WAIT_FOR_DB:-true}" = "true" ]; then
    wait_for_postgres
fi

if [ "${WAIT_FOR_REDIS:-true}" = "true" ] && [ -n "${REDIS_HOST:-}" ]; then
    wait_for_redis
fi

# Check if Nextcloud is already installed
if [ ! -f /var/www/nextcloud/config/config.php ]; then
    log "Nextcloud not yet installed. Running installation..."
    
    # Create database if it doesn't exist
    if [ "${CREATE_DB:-true}" = "true" ]; then
        log "Checking if database exists..."
        if ! PGPASSWORD=${POSTGRES_PASSWORD:-please_change_in_env} psql -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-postgres} -lqt | cut -d \| -f 1 | grep -qw "${POSTGRES_DB:-nextcloud}"; then
            log "Creating database: ${POSTGRES_DB:-nextcloud}"
            PGPASSWORD=${POSTGRES_PASSWORD:-please_change_in_env} psql -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-postgres} -c "CREATE DATABASE \"${POSTGRES_DB:-nextcloud}\";"
            log "Database created."
        else
            log "Database already exists."
        fi
    fi
    
    # Install Nextcloud
    log "Installing Nextcloud..."
    sudo -u www-data php occ maintenance:install \
        --database="pgsql" \
        --database-name="${POSTGRES_DB:-nextcloud}" \
        --database-host="${POSTGRES_HOST:-postgres}" \
        --database-port="${POSTGRES_PORT:-5432}" \
        --database-user="${POSTGRES_USER:-postgres}" \
        --database-pass="${POSTGRES_PASSWORD:-please_change_in_env}" \
        --admin-user="${NEXTCLOUD_ADMIN_USER:-admin}" \
        --admin-pass="${NEXTCLOUD_ADMIN_PASSWORD:-admin}"
    
    # Configure trusted domains
    if [ -n "${NEXTCLOUD_TRUSTED_DOMAINS:-}" ]; then
        log "Setting trusted domains..."
        IFS=',' read -ra DOMAINS <<< "${NEXTCLOUD_TRUSTED_DOMAINS}"
        for i in "${!DOMAINS[@]}"; do
            sudo -u www-data php occ config:system:set trusted_domains $i --value="${DOMAINS[$i]}"
        done
    fi
    
    # Configure Redis if enabled
    if [ -n "${REDIS_HOST:-}" ]; then
        log "Configuring Redis..."
        sudo -u www-data php occ config:system:set redis host --value="${REDIS_HOST}"
        sudo -u www-data php occ config:system:set redis port --value="${REDIS_PORT:-6379}"
        sudo -u www-data php occ config:system:set memcache.locking --value="\\OC\\Memcache\\Redis"
        sudo -u www-data php occ config:system:set memcache.local --value="\\OC\\Memcache\\Redis"
    fi
    
    log "Nextcloud installation completed."
fi

# Set correct permissions
log "Setting correct permissions..."
chown -R www-data:www-data /var/www/nextcloud

# Execute the command passed to docker
log "Executing command: $@"
exec "$@"
