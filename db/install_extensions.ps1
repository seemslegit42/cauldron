# Script to install required PostgreSQL extensions
Write-Host "Installing required PostgreSQL extensions..."

# Function to check if extension is available
function Test-Extension {
    param (
        [string]$ExtensionName
    )
    
    $result = & psql -h localhost -p 5432 -U postgres -d postgres -t -c "SELECT 1 FROM pg_available_extensions WHERE name = '$ExtensionName'"
    return $result -match "1"
}

# Function to install extension from GitHub
function Install-Extension {
    param (
        [string]$ExtensionName,
        [string]$GitHubRepo
    )
    
    $tempDir = "$env:TEMP\$ExtensionName"
    
    # Clone repository
    Write-Host "Cloning $GitHubRepo..."
    & git clone "https://github.com/$GitHubRepo.git" $tempDir
    
    # Build and install
    Push-Location $tempDir
    Write-Host "Building $ExtensionName..."
    & make
    Write-Host "Installing $ExtensionName..."
    & make install
    Pop-Location
    
    # Clean up
    Remove-Item -Recurse -Force $tempDir
}

# Check and install vector extension
if (-not (Test-Extension "vector")) {
    Write-Host "Vector extension not found. Installing..."
    Install-Extension "vector" "pgvector/pgvector"
}

# Check and install TimescaleDB
if (-not (Test-Extension "timescaledb")) {
    Write-Host "TimescaleDB extension not found. Installing..."
    # For TimescaleDB, it's better to use their installer
    Write-Host "Please install TimescaleDB from https://docs.timescale.com/install/latest/self-hosted/installation-windows/"
}

# Check and install other extensions
$coreExtensions = @("uuid-ossp", "pg_trgm", "pgcrypto")
foreach ($ext in $coreExtensions) {
    if (-not (Test-Extension $ext)) {
        Write-Host "$ext extension not found. This should be included in PostgreSQL contrib package."
        Write-Host "Please install the PostgreSQL contrib package."
    }
}

Write-Host "Extension installation completed."