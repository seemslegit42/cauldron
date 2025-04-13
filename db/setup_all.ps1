# Comprehensive script to set up PostgreSQL and the Cauldron sEOS database
Write-Host "Cauldron sEOS Database Setup"
Write-Host "============================"

# Configuration
$DB_NAME = "cauldron_seos"
$DB_USER = "postgres"
$DB_PASSWORD = "password"
$DB_HOST = "localhost"
$DB_PORT = "5432"

# Step 1: Check if PostgreSQL is installed
Write-Host "Step 1: Checking PostgreSQL installation..."
$psqlInstalled = $false
try {
    $psqlVersion = & psql --version
    Write-Host "PostgreSQL client found: $psqlVersion"
    $psqlInstalled = $true
} catch {
    Write-Host "PostgreSQL client not found."
}

# Step 2: Install PostgreSQL if not installed
if (-not $psqlInstalled) {
    Write-Host "Step 2: Installing PostgreSQL..."
    Write-Host "Please download and install PostgreSQL 15 from https://www.postgresql.org/download/windows/"
    Write-Host "During installation, set the password for the postgres user to '$DB_PASSWORD'"
    Write-Host "After installation, please restart this script."
    exit 0
} else {
    Write-Host "Step 2: PostgreSQL is already installed. Skipping."
}

# Step 3: Check if PostgreSQL server is running
Write-Host "Step 3: Checking if PostgreSQL server is running..."
$serverRunning = $false
try {
    $connectionTest = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "SELECT 1" 2>&1
    if ($connectionTest -match "1") {
        Write-Host "PostgreSQL server is running."
        $serverRunning = $true
    } else {
        Write-Host "Failed to connect to PostgreSQL server."
    }
} catch {
    Write-Host "Error connecting to PostgreSQL server: $_"
}

# Step 4: Start PostgreSQL server if not running
if (-not $serverRunning) {
    Write-Host "Step 4: Starting PostgreSQL server..."
    try {
        # Try to start the PostgreSQL service
        Start-Service postgresql-x64-15
        Write-Host "PostgreSQL service started."
    } catch {
        Write-Host "Failed to start PostgreSQL service. Please start it manually."
        Write-Host "After starting the service, please restart this script."
        exit 0
    }
} else {
    Write-Host "Step 4: PostgreSQL server is already running. Skipping."
}

# Step 5: Check if database exists
Write-Host "Step 5: Checking if database exists..."
$dbExists = $false
try {
    $dbCheck = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -t -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" 2>&1
    if ($dbCheck -match "1") {
        Write-Host "Database $DB_NAME already exists."
        $dbExists = $true
    } else {
        Write-Host "Database $DB_NAME does not exist."
    }
} catch {
    Write-Host "Error checking database existence: $_"
}

# Step 6: Create or recreate database
if ($dbExists) {
    Write-Host "Step 6: Database exists. Checking if it should be recreated..."
    $confirm = Read-Host "Do you want to drop and recreate the database? (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Host "Dropping database $DB_NAME..."
        & dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
        $dbExists = $false
    } else {
        Write-Host "Keeping existing database."
    }
} else {
    Write-Host "Step 6: Database does not exist. Will create it."
}

if (-not $dbExists) {
    Write-Host "Creating database $DB_NAME..."
    & createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME -T template0 -E UTF8 -O $DB_USER
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database created successfully."
    } else {
        Write-Host "Failed to create database. Please check PostgreSQL configuration."
        exit 1
    }
}

# Step 7: Install required extensions
Write-Host "Step 7: Installing required extensions..."
$extensionsScript = @"
-- Core extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Try to create vector extension if available
DO \$\$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS vector;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Extension vector is not available. Please install pgvector for full functionality.';
    END;
END
\$\$;

-- Try to create timescaledb extension if available
DO \$\$
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Extension timescaledb is not available. Please install TimescaleDB for full functionality.';
    END;
END
\$\$;
"@

$extensionsScript | Out-File -FilePath "temp_extensions.sql" -Encoding utf8
& psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "temp_extensions.sql"
Remove-Item "temp_extensions.sql"

# Step 8: Create schemas
Write-Host "Step 8: Creating schemas..."
$schemasScript = @"
-- Core business modules
CREATE SCHEMA IF NOT EXISTS erp;
CREATE SCHEMA IF NOT EXISTS hr;
CREATE SCHEMA IF NOT EXISTS crm;

-- Cauldron sEOS modules
CREATE SCHEMA IF NOT EXISTS command_cauldron;
CREATE SCHEMA IF NOT EXISTS synapse;
CREATE SCHEMA IF NOT EXISTS aegis;
CREATE SCHEMA IF NOT EXISTS lore;

-- Technical schemas
CREATE SCHEMA IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS timeseries;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS admin;
CREATE SCHEMA IF NOT EXISTS supabase;
CREATE SCHEMA IF NOT EXISTS realtime;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS integration;
"@

$schemasScript | Out-File -FilePath "temp_schemas.sql" -Encoding utf8
& psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "temp_schemas.sql"
Remove-Item "temp_schemas.sql"

# Step 9: Apply database schema
Write-Host "Step 9: Applying database schema..."
& psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "database_schema.sql"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Database schema applied successfully."
} else {
    Write-Host "Warning: There were some issues applying the database schema."
    Write-Host "Some features may not work correctly."
}

# Step 10: Verify setup
Write-Host "Step 10: Verifying setup..."
$schemaCount = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"
$tableCount = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"

Write-Host "Setup complete!"
Write-Host "Created approximately $schemaCount schemas and $tableCount tables."
Write-Host ""
Write-Host "You can connect to the database using:"
Write-Host "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
Write-Host ""
Write-Host "Note: Some extensions may not be available. For full functionality, please install:"
Write-Host "  - pgvector (https://github.com/pgvector/pgvector)"
Write-Host "  - TimescaleDB (https://docs.timescale.com/install/latest/self-hosted/installation-windows/)"