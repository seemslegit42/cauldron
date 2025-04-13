# Cauldron sEOS Database Setup Script for Windows
# PowerShell version

# Configuration
$DB_NAME = "cauldron_seos"
$DB_USER = "postgres"
$DB_HOST = "localhost"
$DB_PORT = "5432"
$DB_PASSWORD = "password" # Default password, change if needed

# Check if PostgreSQL is installed
try {
    $psqlVersion = & psql --version
    Write-Host "PostgreSQL client found: $psqlVersion"
} catch {
    Write-Host "PostgreSQL client not found. Please install PostgreSQL."
    exit 1
}

# Check if database exists
$dbExists = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'"
if ($dbExists) {
    $confirm = Read-Host "Database $DB_NAME already exists. Do you want to drop and recreate it? (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Host "Dropping database $DB_NAME..."
        & dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
    } else {
        Write-Host "Setup aborted."
        exit 0
    }
}

# Create database
Write-Host "Creating database $DB_NAME..."
& createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME -T template0 -E UTF8 -O $DB_USER

# Check required extensions
Write-Host "Checking required extensions..."
$EXTENSIONS = @("vector", "timescaledb", "uuid-ossp", "pg_trgm", "pgcrypto")
$MISSING_EXTENSIONS = @()

foreach ($ext in $EXTENSIONS) {
    $extExists = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -t -c "SELECT 1 FROM pg_extension WHERE extname = '$ext'"
    if (-not $extExists) {
        $MISSING_EXTENSIONS += $ext
    }
}

if ($MISSING_EXTENSIONS.Count -gt 0) {
    Write-Host "Warning: The following required extensions are not available:"
    foreach ($ext in $MISSING_EXTENSIONS) {
        Write-Host "  - $ext"
    }
    $confirm = Read-Host "Do you want to continue anyway? (y/N)"
    if (-not ($confirm -eq "y" -or $confirm -eq "Y")) {
        Write-Host "Setup aborted."
        exit 1
    }
}

# Apply schema
Write-Host "Applying database schema..."
& psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database_schema.sql

# Verify setup
Write-Host "Verifying setup..."
$SCHEMA_COUNT = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"
$TABLE_COUNT = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"

Write-Host "Setup complete!"
Write-Host "Created $SCHEMA_COUNT schemas and $TABLE_COUNT tables."
Write-Host ""
Write-Host "You can connect to the database using:"
Write-Host "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"