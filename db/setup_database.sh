#!/bin/bash
# Cauldron sEOS Database Setup Script

set -e

# Configuration
DB_NAME="cauldron_seos"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Parse command line arguments
while getopts "n:u:h:p:" opt; do
  case $opt in
    n) DB_NAME="$OPTARG" ;;
    u) DB_USER="$OPTARG" ;;
    h) DB_HOST="$OPTARG" ;;
    p) DB_PORT="$OPTARG" ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

echo "=== Cauldron sEOS Database Setup ==="
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST:$DB_PORT"
echo

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL client not found. Please install PostgreSQL."
    exit 1
fi

# Check if database exists
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    read -p "Database $DB_NAME already exists. Do you want to drop and recreate it? (y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        echo "Dropping database $DB_NAME..."
        dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
    else
        echo "Setup aborted."
        exit 0
    fi
fi

# Create database
echo "Creating database $DB_NAME..."
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" -T template0 -E UTF8 -O "$DB_USER"

# Check required extensions
echo "Checking required extensions..."
EXTENSIONS=("vector" "timescaledb" "uuid-ossp" "pg_trgm" "pgcrypto")
MISSING_EXTENSIONS=()

for ext in "${EXTENSIONS[@]}"; do
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -tc "SELECT 1 FROM pg_extension WHERE extname = '$ext'" | grep -q 1; then
        MISSING_EXTENSIONS+=("$ext")
    fi
done

if [ ${#MISSING_EXTENSIONS[@]} -ne 0 ]; then
    echo "Warning: The following required extensions are not available:"
    for ext in "${MISSING_EXTENSIONS[@]}"; do
        echo "  - $ext"
    done
    read -p "Do you want to continue anyway? (y/N): " confirm
    if [[ ! ($confirm == [yY] || $confirm == [yY][eE][sS]) ]]; then
        echo "Setup aborted."
        exit 1
    fi
fi

# Apply schema
echo "Applying database schema..."

# Option 1: Apply complete schema at once
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f database_schema.sql

# Option 2: Apply individual schema files (commented out by default)
# echo "Applying initialization scripts..."
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 00_init/00_extensions.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 00_init/01_schemas.sql
# 
# echo "Applying core schema..."
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 01_core/01_users.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 01_core/02_roles_permissions.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 01_core/03_organizations.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 01_core/04_audit_settings.sql
# 
# echo "Applying Lore module schema..."
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 02_lore/01_documents.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 02_lore/02_knowledge_graph.sql
# 
# echo "Applying TimeSeries module schema..."
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 03_timeseries/01_metrics.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 03_timeseries/02_events.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 03_timeseries/03_forecasting.sql
# 
# echo "Applying Vector module schema..."
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 04_vector/01_embeddings.sql
# 
# echo "Applying Supabase integration schema..."
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 05_supabase/01_auth.sql
# psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 05_supabase/02_storage.sql

# Verify setup
echo "Verifying setup..."
SCHEMA_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tc "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')")
TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')")

echo "Setup complete!"
echo "Created $SCHEMA_COUNT schemas and $TABLE_COUNT tables."
echo
echo "You can connect to the database using:"
echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"