# PowerShell script to create custom Cauldron apps
Write-Host "Creating custom Cauldron apps..."

# Set variables
$BENCH_DIR_NAME = "frappe-bench"
$CUSTOM_APPS = @(
    "cauldron_operations_core",
    "cauldron_synapse",
    "cauldron_aegis_protocol",
    "cauldron_lore",
    "cauldron_command_cauldron"
)

# Check if the bench directory exists
$CURRENT_DIR = (Get-Location).Path
$BENCH_PATH = Join-Path $CURRENT_DIR $BENCH_DIR_NAME

if (-not (Test-Path $BENCH_PATH)) {
    Write-Host "Bench directory not found. Please run download-frappe-bench.ps1 first."
    exit 1
}

# Create custom apps
foreach ($APP_NAME in $CUSTOM_APPS) {
    Write-Host "Creating custom app: $APP_NAME"
    $APPS_PATH = Join-Path $BENCH_PATH "apps"
    $APP_PATH = Join-Path $APPS_PATH $APP_NAME
    
    if (Test-Path $APP_PATH) {
        Write-Host "App $APP_NAME already exists. Skipping creation."
        continue
    }
    
    # Create the app directory
    New-Item -ItemType Directory -Path $APP_PATH
    
    # Create basic directory structure for the app
    New-Item -ItemType Directory -Path "$APP_PATH\$APP_NAME" -Force
    New-Item -ItemType Directory -Path "$APP_PATH\$APP_NAME\api" -Force
    New-Item -ItemType Directory -Path "$APP_PATH\$APP_NAME\public\js" -Force
    New-Item -ItemType Directory -Path "$APP_PATH\$APP_NAME\public\css" -Force
    
    # Create a basic controller file
    $CONTROLLER_CONTENT = @"
import frappe
from frappe import _

@frappe.whitelist()
def get_status():
    return {
        "status": "success",
        "message": _("$APP_NAME module is active"),
        "module": "$APP_NAME"
    }
"@
    $CONTROLLER_CONTENT | Out-File -FilePath "$APP_PATH\$APP_NAME\api\controller.py" -Encoding utf8
    
    # Create a basic __init__.py file
    $INIT_CONTENT = @"
__version__ = '0.0.1'
"@
    $INIT_CONTENT | Out-File -FilePath "$APP_PATH\$APP_NAME\__init__.py" -Encoding utf8
    
    # Create a basic hooks.py file
    $APP_TITLE = ($APP_NAME -replace '_', ' ') -replace '\b\w', { $args[0].Value.ToUpper() }
    $HOOKS_CONTENT = @"
app_name = "$APP_NAME"
app_title = "$APP_TITLE"
app_publisher = "Cauldron"
app_description = "$APP_TITLE module for Cauldron"
app_email = "info@cauldron.io"
app_license = "MIT"
"@
    $HOOKS_CONTENT | Out-File -FilePath "$APP_PATH\$APP_NAME\hooks.py" -Encoding utf8
    
    # Create a basic setup.py file
    $SETUP_CONTENT = @"
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="$APP_NAME",
    version="0.0.1",
    description="$(($APP_NAME -replace '_', ' ') -replace '\b\w', { $args[0].Value.ToUpper() }) module for Cauldron",
    author="Cauldron",
    author_email="info@cauldron.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
"@
    $SETUP_CONTENT | Out-File -FilePath "$APP_PATH\setup.py" -Encoding utf8
    
    # Create a basic requirements.txt file
    $REQUIREMENTS_CONTENT = @"
frappe
"@
    $REQUIREMENTS_CONTENT | Out-File -FilePath "$APP_PATH\requirements.txt" -Encoding utf8
    
    # Create a basic README.md file
    $README_CONTENT = @"
# $(($APP_NAME -replace '_', ' ') -replace '\b\w', { $args[0].Value.ToUpper() })

$(($APP_NAME -replace '_', ' ') -replace '\b\w', { $args[0].Value.ToUpper() }) module for Cauldron

## Installation

1. Install Frappe Bench
2. Add the app to your bench:
   ```
   bench get-app $APP_NAME https://github.com/cauldron/$APP_NAME
   ```
3. Install the app on your site:
   ```
   bench --site your-site install-app $APP_NAME
   ```

## Features

- Feature 1
- Feature 2
- Feature 3

## License

MIT
"@
    $README_CONTENT | Out-File -FilePath "$APP_PATH\README.md" -Encoding utf8
    
    Write-Host "Custom app $APP_NAME created successfully."
}

Write-Host "Custom Cauldron apps creation completed."