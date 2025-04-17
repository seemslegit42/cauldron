# PowerShell script to set up a new site in the Frappe bench
Write-Host "Setting up a new site in the Frappe bench..."

# Set variables
$BENCH_DIR_NAME = "frappe-bench"
$SITE_NAME = "cauldron.local"
$ADMIN_PASSWORD = "admin"

# Check if the bench directory exists
$CURRENT_DIR = (Get-Location).Path
$BENCH_PATH = Join-Path $CURRENT_DIR $BENCH_DIR_NAME

if (-not (Test-Path $BENCH_PATH)) {
    Write-Host "Bench directory not found. Please run download-frappe-bench.ps1 first."
    exit 1
}

# Create a new site
Write-Host "Creating a new site: $SITE_NAME"
$SITES_PATH = Join-Path $BENCH_PATH "sites"
$SITE_PATH = Join-Path $SITES_PATH $SITE_NAME

if (Test-Path $SITE_PATH) {
    Write-Host "Site already exists: $SITE_PATH"
} else {
    # Create the site directory
    New-Item -ItemType Directory -Path $SITE_PATH

    # Create a basic site configuration
    $SITE_CONFIG = @"
{
    "db_name": "cauldron",
    "db_password": "frappe",
    "admin_password": "$ADMIN_PASSWORD"
}
"@
    $SITE_CONFIG | Out-File -FilePath "$SITE_PATH\site_config.json" -Encoding utf8

    # Create a basic site_config.json file
    Write-Host "Site created: $SITE_PATH"
}

# Create a basic README.md file with instructions
$README_CONTENT = @"
# Frappe Bench for Cauldron

This is a pre-built Frappe bench for the Cauldron project.

## Structure

- `apps/` - Contains all Frappe applications
- `sites/` - Contains site configurations and data
- `config/` - Contains configuration files for the bench
- `logs/` - Contains log files

## Getting Started

1. Install the required dependencies:
   - Python 3.11
   - Node.js 18
   - Redis
   - PostgreSQL

2. Set up a virtual environment:
   ```
   cd $BENCH_DIR_NAME
   python -m venv env
   .\env\Scripts\activate
   pip install -e apps/frappe
   ```

3. Install Node.js dependencies:
   ```
   cd apps/frappe
   yarn install
   ```

4. Start the development server:
   ```
   cd $BENCH_DIR_NAME
   bench start
   ```

5. Access the site at: http://localhost:8000

## Documentation

For more information, refer to the Frappe documentation: https://frappeframework.com/docs
"@
$README_CONTENT | Out-File -FilePath "$BENCH_PATH\README.md" -Encoding utf8

Write-Host "Frappe site setup completed. The site is available at: $SITE_PATH"
Write-Host "You can now follow the instructions in the README.md file to start the development server."