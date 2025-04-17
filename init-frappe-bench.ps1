# PowerShell script to initialize Frappe bench using Docker
Write-Host "Initializing Frappe bench using Docker..."

# Set variables
$BENCH_DIR_NAME = "frappe-bench"
$FRAPPE_BRANCH = "version-15"
$PYTHON_VERSION = "python3.11"

# Create a temporary Dockerfile for initializing the bench
$DOCKERFILE_CONTENT = @"
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and Yarn
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && npm install -g yarn \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash frappe && \
    echo "frappe ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/frappe

# Install bench
RUN pip install --no-cache-dir frappe-bench

# Switch to non-root user
USER frappe
WORKDIR /home/frappe

# Initialize bench
RUN bench init --frappe-branch $FRAPPE_BRANCH --python /usr/local/bin/python3 --skip-redis-config-generation $BENCH_DIR_NAME

# Copy bench files to a volume
VOLUME /bench-output
CMD cp -r /home/frappe/$BENCH_DIR_NAME/* /bench-output/
"@

# Create a temporary directory for Docker build
$TEMP_DIR = "temp-frappe-init"
if (-not (Test-Path $TEMP_DIR)) {
    New-Item -ItemType Directory -Path $TEMP_DIR
}

# Write Dockerfile to temporary directory
$DOCKERFILE_CONTENT | Out-File -FilePath "$TEMP_DIR/Dockerfile" -Encoding utf8

# Build the Docker image
Write-Host "Building Docker image for Frappe bench initialization..."
docker build -t frappe-bench-init $TEMP_DIR

# Run the Docker container to initialize the bench
Write-Host "Running Docker container to initialize Frappe bench..."
$CURRENT_DIR = (Get-Location).Path
$BENCH_PATH = Join-Path $CURRENT_DIR $BENCH_DIR_NAME
docker run --rm -v "${BENCH_PATH}:/bench-output" frappe-bench-init

# Clean up
Write-Host "Cleaning up temporary files..."
Remove-Item -Recurse -Force $TEMP_DIR

Write-Host "Frappe bench initialization completed. The bench is available in the $BENCH_DIR_NAME directory."