# Check if PostgreSQL is installed and running
try {
    $psqlVersion = & psql --version
    Write-Host "PostgreSQL client found: $psqlVersion"
    
    # Try to connect to PostgreSQL
    $connectionTest = & psql -h localhost -p 5432 -U postgres -c "SELECT version()" 2>&1
    if ($connectionTest -match "PostgreSQL") {
        Write-Host "Successfully connected to PostgreSQL server"
        Write-Host $connectionTest
    } else {
        Write-Host "Failed to connect to PostgreSQL server. Error:"
        Write-Host $connectionTest
    }
} catch {
    Write-Host "PostgreSQL client not found or error occurred. Please install PostgreSQL."
    Write-Host "Error: $_"
}