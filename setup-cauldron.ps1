# PowerShell script to set up the Cauldron project
Write-Host "Setting up the Cauldron project..."

# Run the download-frappe-bench.ps1 script
Write-Host "Step 1: Downloading and setting up the Frappe bench..."
powershell -ExecutionPolicy Bypass -File ./download-frappe-bench.ps1

# Run the setup-frappe-site.ps1 script
Write-Host "Step 2: Setting up a new site in the Frappe bench..."
powershell -ExecutionPolicy Bypass -File ./setup-frappe-site.ps1

# Run the create-cauldron-apps.ps1 script
Write-Host "Step 3: Creating custom Cauldron apps..."
powershell -ExecutionPolicy Bypass -File ./create-cauldron-apps.ps1

Write-Host "Cauldron project setup completed."
Write-Host "Follow the instructions in the frappe-bench/README.md file to start the development server."