# Script to install PostgreSQL on Windows
Write-Host "Installing PostgreSQL on Windows..."

# Check if PostgreSQL is already installed
try {
    $psqlVersion = & psql --version
    Write-Host "PostgreSQL client is already installed: $psqlVersion"
    Write-Host "Skipping installation."
    exit 0
} catch {
    Write-Host "PostgreSQL client not found. Proceeding with installation..."
}

# Download PostgreSQL installer
$installerUrl = "https://get.enterprisedb.com/postgresql/postgresql-15.4-1-windows-x64.exe"
$installerPath = "$env:TEMP\postgresql_installer.exe"

Write-Host "Downloading PostgreSQL installer..."
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

# Install PostgreSQL silently
Write-Host "Installing PostgreSQL..."
$installArgs = "--mode unattended --superpassword password --servicename PostgreSQL --servicepassword password --serverport 5432"
Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait

# Add PostgreSQL bin directory to PATH
$pgBinPath = "C:\Program Files\PostgreSQL\15\bin"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")

if (-not $currentPath.Contains($pgBinPath)) {
    Write-Host "Adding PostgreSQL bin directory to PATH..."
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$pgBinPath", "Machine")
}

Write-Host "PostgreSQL installation completed."
Write-Host "Please restart your PowerShell session for PATH changes to take effect."