# PowerShell script to download a pre-built Frappe bench from GitHub
Write-Host "Downloading Frappe bench from GitHub..."

# Set variables
$BENCH_DIR_NAME = "frappe-bench"
$FRAPPE_BRANCH = "version-15"
$TEMP_DIR = "temp-frappe-download"

# Create a temporary directory for download
if (-not (Test-Path $TEMP_DIR)) {
    New-Item -ItemType Directory -Path $TEMP_DIR
}

# Download the Frappe repository
Write-Host "Downloading Frappe repository..."
$CURRENT_DIR = (Get-Location).Path
$BENCH_PATH = Join-Path $CURRENT_DIR $BENCH_DIR_NAME

# Check if the bench directory already exists
if (Test-Path $BENCH_PATH) {
    Write-Host "Bench directory already exists. Removing it..."
    Remove-Item -Recurse -Force $BENCH_PATH
}

# Create the bench directory
New-Item -ItemType Directory -Path $BENCH_PATH

# Clone the Frappe repository
Write-Host "Cloning Frappe repository..."
cd $TEMP_DIR
git clone https://github.com/frappe/frappe.git --branch $FRAPPE_BRANCH --depth 1
cd ..

# Copy the Frappe repository to the bench directory
Write-Host "Setting up bench directory structure..."
New-Item -ItemType Directory -Path "$BENCH_PATH\apps"
New-Item -ItemType Directory -Path "$BENCH_PATH\sites"
New-Item -ItemType Directory -Path "$BENCH_PATH\config"
New-Item -ItemType Directory -Path "$BENCH_PATH\logs"

# Copy the Frappe app to the bench directory
Write-Host "Copying Frappe app to bench directory..."
New-Item -ItemType Directory -Path "$BENCH_PATH\apps\frappe"
Copy-Item -Recurse "$TEMP_DIR\frappe\*" "$BENCH_PATH\apps\frappe"

# Create a basic site configuration
Write-Host "Creating basic site configuration..."
$SITE_CONFIG = @"
{
    "db_host": "localhost",
    "redis_cache": "redis://localhost:6379/0",
    "redis_queue": "redis://localhost:6379/1",
    "redis_socketio": "redis://localhost:6379/2",
    "socketio_port": 9000,
    "webserver_port": 8000,
    "developer_mode": 1,
    "serve_default_site": true,
    "auto_update": false,
    "frappe_user": "frappe",
    "shallow_clone": true
}
"@
$SITE_CONFIG | Out-File -FilePath "$BENCH_PATH\sites\common_site_config.json" -Encoding utf8

# Clean up
Write-Host "Cleaning up temporary files..."
Remove-Item -Recurse -Force $TEMP_DIR

Write-Host "Frappe bench setup completed. The bench is available in the $BENCH_DIR_NAME directory."