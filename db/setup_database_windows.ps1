# Cauldron sEOS Database Setup Script for Windows
# PowerShell version

# Configuration
$DB_NAME = "cauldron_seos"
$DB_USER = "postgres"
$DB_HOST = "localhost"
$DB_PORT = "5432"
$DB_PASSWORD = "password" # Default password, change if needed

# Function to execute SQL commands
function Execute-SQL {
    param (
        [string]$Database,
        [string]$Command
    )
    
    $result = & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $Database -c $Command
    return $result
}

# Check if PostgreSQL is installed
try {
    $psqlVersion = & psql --version
    Write-Host "PostgreSQL client found: $psqlVersion"
} catch {
    Write-Host "PostgreSQL client not found. Please install PostgreSQL."
    exit 1
}

# Check if database exists
$dbExists = Execute-SQL "postgres" "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'"
if ($dbExists -match "1") {
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

# Install core extensions
Write-Host "Installing core extensions..."
& psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f install_extensions.sql

# Create schemas
Write-Host "Creating schemas..."
$schemas = @(
    "erp", "hr", "crm", "command_cauldron", "synapse", "aegis", "lore",
    "vector", "timeseries", "audit", "admin", "supabase", "realtime",
    "storage", "auth", "analytics", "integration"
)

foreach ($schema in $schemas) {
    Write-Host "Creating schema: $schema"
    Execute-SQL $DB_NAME "CREATE SCHEMA IF NOT EXISTS $schema"
}

# Apply schema
Write-Host "Applying database schema..."
& psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database_schema.sql

# Verify setup
Write-Host "Verifying setup..."
$SCHEMA_COUNT = Execute-SQL $DB_NAME "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"
$TABLE_COUNT = Execute-SQL $DB_NAME "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')"

Write-Host "Setup complete!"
Write-Host "Created schemas and tables."
Write-Host ""
Write-Host "You can connect to the database using:"
Write-Host "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"